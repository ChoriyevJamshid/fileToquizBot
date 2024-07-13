import csv
import pandas as pd
import PyPDF2


async def get_csv_content(file_path):
    result = []
    try:
        with open(file_path, mode="r") as csv_file:
            data = data = [row for row in csv.reader(csv_file, delimiter=",")]

        for row in data:
            if len(row) == 1 and row[0] != '':
                result.append(row[0])
    except Exception:
        pass

    return result


