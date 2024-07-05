# import pandas as pd
#
#
# def get_excel_content(file_path, _format):
#     result = []
#     engine = "xlrd" if _format == "xls" else "openpyxl"
#     df = pd.read_excel(file_path, engine=engine)
#     for value in df.values:
#         result.append(value[0])
#     return result
#
#
# result = get_excel_content("Педагогика. Психология 2022.xls", "xls")
# print(result)


import string

# import string
# import random


# name = str()
# tpl = 'upper', 'lower'
# for i in range(6):
#     stm = random.choice(tpl)
#     if stm == 'upper':
#         name += random.choice(string.ascii_uppercase)
#     else:
#         name += random.choice(string.ascii_lowercase)
# return name

# def generate_random_string():
#     tpl = 'upper', 'lower'
#     result = ""
#     for i in range(6):
#         stm = random.choice(tpl)
#         if stm == 'upper':
#             result += random.choice(string.ascii_uppercase)
#         else:
#             result += random.choice(string.ascii_lowercase)




