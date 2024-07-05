import string
import random


def generate_random_string(length=10):
    upper = list(string.ascii_uppercase)
    lower = list(string.ascii_lowercase)
    digits = list(string.digits)
    mixes = upper + lower + digits
    random.shuffle(mixes)
    result = ""
    for i in range(length):
        result += random.choice(mixes)
    return result


def get_current_option_id(current_option: str, options: list):
    for index, option in enumerate(options):
        if option == current_option:
            return index


print(get_current_option_id('1', ['2', '3', '1', '4']))

correct_option_id = lambda options, correct_option: [option_id for option_id, option in enumerate(options) if option == correct_option][0]

print(correct_option_id(['2', '3', '1', '4'], '1'))
