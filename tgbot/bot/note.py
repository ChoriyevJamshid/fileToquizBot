import random


def create_txt_questions(number=80):
    with open(f"questions_txt_{number}.txt", mode='w', encoding='utf-8') as txt_file:
        for i in range(number):
            correct = 2 * (i + 1)

            for j in range(5):
                if j == 0:
                    value = f"?{i + 1} + {i + 1} = ?\n"
                elif j == 1:
                    value = f"*{correct}\n"
                else:
                    value = f"{random.randint(1, 100)}\n"
                    if j == 4:
                        value += "\n"
                txt_file.write(value)


if __name__ == "__main__":
    create_txt_questions(20)
