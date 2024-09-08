import asyncio
import docx
from pprint import pprint


async def get_docx_content(file_path):
    document = docx.Document(file_path)
    result = []
    question_data = {
        "question": None,
        "options": [],
        "correct_option": None,
        "correct_option_id": None
    }
    iterator = 0
    try:
        for paragraph in document.paragraphs:
            # print(paragraph.text)
            text = str(paragraph.text).strip()[:100]
            if not text:
                continue

            if text.startswith("?"):
                question = text.split("?", maxsplit=1)[-1]
                question_data["question"] = question
                question_data["options"] = []
                iterator = 0

            elif text.startswith("*"):
                correct_option = text.split("*", maxsplit=1)[-1]
                question_data["correct_option"] = correct_option
                question_data["correct_option_id"] = iterator - 1
                question_data['options'].append(correct_option)

            else:
                question_data["options"].append(text)

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
    result = await get_docx_content("C:/Users/user/OneDrive/Desktop/question.docx")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())




