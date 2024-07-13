import pandas as pd


async def get_excel_content(file_path, _format):
    result = []
    engine = "xlrd" if _format == "xls" else "openpyxl"
    df = pd.read_excel(file_path, engine=engine)
    try:
        result.append(df.head().columns.values[0])
        for value in df.values:
            result.append(value[0])
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
            result.append(value[0])
    except Exception as e:
        pass
    return result


# print(get_excel_content_sync("matematika 1.xlsx", "xlsx"))
