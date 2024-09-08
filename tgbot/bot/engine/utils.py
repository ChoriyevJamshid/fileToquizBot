import csv
import pandas as pd
import PyPDF2

import PyPDF2

# Open the PDF file
with open('C:/Users/user/OneDrive/Desktop/========.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)

    # Iterate through each page
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()

        # Split the text into lines and print each line
        for line in text.splitlines():
            line = line.strip()
            print(repr(line))
