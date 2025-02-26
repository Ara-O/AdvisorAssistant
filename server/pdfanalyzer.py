# from langchain.document_loaders import PyMuPDFLoader

# pdf_path = "eval.pdf"
# loader = PyMuPDFLoader(pdf_path)
# documents = loader.load()

# # Print extracted text
# for doc in documents:
#     print(doc.page_content)













# TRIED BUT TRASH

# -----------------------

# from langchain_community.document_loaders import PDFPlumberLoader

# loader = PDFPlumberLoader("eval.pdf")
# documents = loader.load()

# for doc in documents:
#     print(doc.page_content)

# --------------------------------------

# from langchain.document_loaders import PDFMinerLoader

# loader = PDFMinerLoader("eval.pdf")
# documents = loader.load()

# for doc in documents:
#     print(doc.page_content)

# -------------------------

# from tabula import read_pdf

# # Extract tables from all pages
# tables = read_pdf("eval.pdf", pages="all")

# # Print extracted tables
# for i, table in enumerate(tables):
#     print(f"Table {i+1}:\n", table)

#- --------------------------------

# PRETTY OKAY

import camelot

tables = camelot.read_pdf("eval.pdf", pages="all", line_scale=50)
for i, table in enumerate(tables):
    print(f"Table {i}:\n", table.df) 
    print("\n--------------------------------\n")
