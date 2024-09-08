import asyncio
import pandas as pd
from pprint import pprint


# async def get_excel_content(file_path, _format):
#     result = []
#     engine = "xlrd" if _format == "xls" else "openpyxl"
#     df = pd.read_excel(file_path, engine=engine)
#     try:
#         result.append(df.head().columns.values[0])
#         for value in df.values:
#             result.append(value[0])
#     except Exception as e:
#         pass
#     return result
#
#
#
# def get_excel_content_sync(file_path, _format):
#     result = []
#     engine = "xlrd" if _format == "xls" else "openpyxl"
#     df = pd.read_excel(file_path, engine=engine)
#     try:
#         result.append(df.head().columns.values[0])
#         for value in df.values:
#             result.append(value[0])
#     except Exception as e:
#         pass
#     return result


async def get_excel_content(file_path, _format):
    result = []
    question_data = {
        "question": None,
        "options": [],
        "correct_option": None,
        "correct_option_id": None
    }
    iterator = 0

    engine = "xlrd" if _format == "xls" else "openpyxl"
    df = pd.read_excel(file_path, engine=engine)
    try:

        for value in df.values:
            value = str(value[0]).strip()

            if value == 'nan':
                continue

            value = str(value)[:100]
            if value.startswith("?"):
                question = value.split("?", maxsplit=1)[-1]
                question_data["question"] = question
                question_data["options"] = []
                iterator = 0

            elif value.startswith("*"):
                correct_option = value.split("*", maxsplit=1)[-1]
                question_data["correct_option"] = correct_option
                question_data["correct_option_id"] = iterator - 1
                question_data['options'].append(correct_option)

            else:
                question_data["options"].append(value)

            iterator += 1
            if iterator > 4:
                iterator = 0

            if question_data["question"] is not None and question_data["correct_option"] is not None \
                    and question_data["correct_option_id"] is not None and len(question_data["options"]) == 4:
                result.append(question_data)
                question_data = {
                    "question": None,
                    "options": [],
                    "correct_option": None,
                    "correct_option_id": None
                }

    except Exception as e:
        pass

    return result


async def main():
    result = await get_excel_content("C:/Users/user/OneDrive/Desktop/Лист Microsoft Excel.xlsx", "xlsx")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
