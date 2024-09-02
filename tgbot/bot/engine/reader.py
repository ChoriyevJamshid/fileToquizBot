import asyncio
import pandas as pd
import docx
import csv
from pprint import pprint


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
    _num = len(result) // 5
    return result[:_num * 5]


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
    _num = len(result) // 5
    return result[:_num * 5]


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
    _num = len(result) // 5
    return result[:_num * 5]


async def get_txt_content(file_path):
    result = []
    question_data = {
        "question": None,
        "options": [],
        "correct_option": None,
        "correct_option_id": None
    }
    iterator = 0

    try:
        with open(file_path, mode="r", encoding="utf-8") as txt_file:
            for line in txt_file:
                line = line.strip()
                if not line:
                    continue

                value = str(line)[:100]
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

                if question_data["question"] and question_data["correct_option"] \
                    and question_data["correct_option_id"] and len(question_data["options"]) == 4:
                    result.append(question_data)
                    question_data = {
                        "question": None,
                        "options": [],
                        "correct_option": None,
                        "correct_option_id": None
                    }

    except FileNotFoundError:
        pass
    _num = len(result) // 5
    return result[:_num * 5]


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
    _num = len(result) // 5
    return result[:_num * 5]



async def main():
    result = await get_txt_content("/home/jamshid/Desktop/question.txt")
    pprint(result)

if __name__ == "__main__":
    asyncio.run(main())
    # text = "hello world?"
    # print(text.split("?", 1))
