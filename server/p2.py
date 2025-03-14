from bs4 import BeautifulSoup
import pandas as pd
import base64
from email import message_from_binary_file
from bs4 import BeautifulSoup
# from sql_client import find_element
from flask import jsonify
import re 

# Step 1: Read and parse the MHTML file
with open(mhtml_file, 'rb') as file:
    msg = message_from_binary_file(file)
    
# Step 2: Find and decode the HTML part
html_part = None

for part in msg.walk():
    if part.get_content_type() == "text/html":
        html_part = part.get_payload(decode=True)
        break

if html_part is None:
    print("No HTML part found in the MHTML file.")
    # return jsonify({"message": "There was no HTML found"}), 400

# Decode HTML content if it is base64-encoded
try:
    html_content = base64.b64decode(html_part).decode('utf-8')
    
except:
    html_content = html_part.decode('utf-8')

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")
all_tables = soup.findAll("tbody")

print(len(all_tables))

def parse_html_table(table):
    """
    Parse an HTML table handling rowspans and colspans.
    Returns a list of rows (each row is a list of cell texts).
    """
    rows = table.find_all("tr")
    grid = []
    # Dictionary to track cells with rowspan that should appear in future rows.
    # Keys are (row_index, col_index) tuples.
    spanning = {}
    
    for row_index, row in enumerate(rows):
        cells = row.find_all("td")
        row_data = []
        col = 0
        # Check if any cell from previous row spans into this row.
        while (row_index, col) in spanning:
            row_data.append(spanning[(row_index, col)])
            col += 1
        
        for cell in cells:
            # Remove header divs (e.g., the "Met", "Requirement", etc. labels)
            for header in cell.find_all("div", class_="xe-col-xs"):
                header.decompose()
            text = cell.get_text(separator=" ", strip=True)
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))
            
            # Fill in the cell (and duplicate if colspan > 1)
            for i in range(col, col + colspan):
                row_data.append(text)
                # If rowspan > 1, mark this cell for the following rows.
                if rowspan > 1:
                    for j in range(1, rowspan):
                        spanning[(row_index + j, i)] = text
            col += colspan
        grid.append(row_data)
    return grid

all_reqs = []
# Define the column names in the desired order
columns = ["met", "requirement", "term", "satisfied_by", "title", "attribute", "credits", "grade", "source"]

for tbody in all_tables:
    # Parse the table and create a grid of cells
    grid = parse_html_table(tbody)


    # Convert grid rows into a list of dictionaries.
    # If a row has fewer than 9 columns (due to rowspan), we fill missing values from previous row if needed.
    parsed_data = []
    last_row = {}
    for row in grid:
        # Pad row if necessary
        if len(row) < len(columns):
            row += [""] * (len(columns) - len(row))
        # For the 'met' and 'requirement' columns, if empty, inherit from the last row.
        current = dict(zip(columns, row[:len(columns)]))
        if not current["met"]:
            current["met"] = last_row.get("met", "")
        if not current["requirement"]:
            current["requirement"] = last_row.get("requirement", "")
        parsed_data.append(current)
        last_row = current

    # Create a DataFrame to display the parsed table
    df = pd.DataFrame(parsed_data, columns=columns)
    # print(df)
    all_reqs.extend(parsed_data)
    
all_reqs_df = pd.DataFrame(all_reqs, columns=columns)
all_reqs_df = all_reqs_df[all_reqs_df["met"].isin(["Yes", "No"])]
# all_reqs_df = all_reqs_df[all_reqs_df["requirement"].str.len() >= 4]
pattern = r'^\s*\d+(\.\d+)?\s*$'

# Filter out rows where 'requirement' matches the decimal string pattern
all_reqs_df = all_reqs_df[~all_reqs_df["requirement"].str.match(pattern, na=False)]
all_reqs_df = all_reqs_df.drop_duplicates()
