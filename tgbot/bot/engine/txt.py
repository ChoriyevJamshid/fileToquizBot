import asyncio
from pprint import pprint


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

                if question_data["question"] is not None and question_data["correct_option"] is not None \
                        and question_data["correct_option_id"] is not None and len(question_data["options"]) == 4:
                    result.append(question_data)
                    question_data = {
                        "question": None,
                        "options": [],
                        "correct_option": None,
                        "correct_option_id": None
                    }

    except FileNotFoundError:
        pass

    return result


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
