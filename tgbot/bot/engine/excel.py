import pandas as pd


async def get_excel_content(file_path, _format):
    result = []
    engine = "xlrd" if _format == "xls" else "openpyxl"
    df = pd.read_excel(file_path, engine=engine)
    for value in df.values:
        result.append(value[0])
    return result
