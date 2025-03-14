from bs4 import BeautifulSoup
import pandas as pd

# Your HTML content (for example, read from a file or defined as a string)
html_content = """

"""

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")
tbody = soup.find("tbody")

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

# Parse the table and create a grid of cells
grid = parse_html_table(tbody)

# Define the column names in the desired order
columns = ["met", "requirement", "term", "satisfied_by", "title", "attribute", "credits", "grade", "source"]

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
print(df)