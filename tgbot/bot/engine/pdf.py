import asyncio
import PyPDF2


async def get_pdf_content(file_path: str) -> list:
    result = []
    question_data = {
        "question": None,
        "options": [],
        "correct_option": None,
        "correct_option_id": None
    }
    iterator = 0
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()

                for line in text.splitlines():
                    value = line.strip()[:100]

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
    result = await get_pdf_content("C:/Users/user/OneDrive/Desktop/========.pdf")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
