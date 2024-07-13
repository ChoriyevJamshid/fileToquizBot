import pandas as pd
import docx
import csv


async def get_excel_content(file_path, _format):
    result = []
    engine = "xlrd" if _format == "xls" else "openpyxl"
    df = pd.read_excel(file_path, engine=engine)
    try:
        result.append(df.head().columns.values[0])
        for value in df.values:
            value = str(value[0])[:100]
            result.append(value)
    except Exception as e:
        pass
    return result


def get_excel_content_sync(file_path, _format):
    result = []
    engine = "xlrd" if _format == "xls" else "openpyxl"
    df = pd.read_excel(file_path, engine=engine)
    try:
        result.append(df.head().columns.values[0])
        for value in df.values:
            value = str(value[0])[:100]
            result.append(value)
    except Exception as e:
        pass
    return result


async def get_docx_content(file_path):
    document = docx.Document(file_path)
    result = []
    try:
        for paragraph in document.paragraphs:
            if paragraph.text != '':
                value = str(paragraph.text)[:100]
                result.append(value)
    except Exception as e:
        pass
    return result


async def get_txt_content(file_path):
    result = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as txt_file:
            for line in txt_file:
                line = line.strip()
                if line:
                    value = str(line)[:100]
                    result.append(value)

    except FileNotFoundError:
        pass
    return result


async def get_csv_content(file_path):
    result = []
    try:
        with open(file_path, mode="r") as csv_file:
            data = data = [row for row in csv.reader(csv_file, delimiter=",")]

        for row in data:
            if len(row) == 1 and row[0] != '':
                value = str(row[0])[:100]
                result.append(value)
    except Exception:
        pass
    return result

