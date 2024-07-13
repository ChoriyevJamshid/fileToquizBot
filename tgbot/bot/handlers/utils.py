import string
import random
import re
# import time
from typing import List, Dict
from pprint import pprint


# from random import shuffle
# import time
# from pprint import pprint as print
#
# index = 0
# current = {
#     'start_time': time.perf_counter()
# }
# time.sleep(2)
# end_time = time.perf_counter()
# users = {
#     "5671504436": {
#         "user_id": 5671504436,
#         "username": "<[>@@@@<]>",
#         "spend_time": 0,
#         "corrects": 0,
#         "skips": 0,
#         "quizzes": {}
#     },
#     "2124744962": {
#         "user_id": 2124744962,
#         "username": "@jamshidchoriyevDev",
#         "spend_time": 0,
#         "corrects": 0,
#         "skips": 0,
#         "quizzes": {}
#     }
# }
# print(users)
# for user, user_data in users.items():
#     user_id = user_data['user_id']
#     quizzes = user_data['quizzes']
#     if quizzes.get(index):
#         continue
#
#     quizzes[index] = {
#         "is_correct": None,
#         "start_time": current['start_time'],
#         "end_time": end_time,
#         "spend_time": round(current['start_time'] - end_time, 1)
#     }
#
#     user_data['quizzes'] = quizzes
#     user_data['skips'] += 1
# print('\n')
# print(users)


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


def get_time(seconds: int, texts: dict, language: str):
    if seconds < 60:
        return f"{round(seconds)} {texts['seconds'][language]}"
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)} {texts['minute'][language]} {int(seconds)} {texts['seconds'][language]}"


def search_user(users_list, low, high, user_id):
    if high >= low:

        mid = low + (high - low) // 2

        if users_list[mid]['user_id'] == user_id:
            return True

        elif users_list[mid]['user_id'] > user_id:
            return search_user(users_list, low, mid - 1, user_id)

        else:
            return search_user(users_list, mid + 1, high, user_id)

    else:
        return False


def username_filtering(username: str) -> str:
    pattern = r"<([^<>]*?)>"
    replacement = r"(\1)"

    return re.sub(pattern, replacement, username)


class MergeSort:
    @staticmethod
    def merge(users, left: int, mid: int, right: int):
        sub_array_one = mid - left + 1
        sub_array_two = right - mid

        left_array = [{"user_id": ""}] * sub_array_one
        right_array = [{"user_id": ""}] * sub_array_two

        for i in range(sub_array_one):
            left_array[i] = users[left + i]
        for j in range(sub_array_two):
            right_array[j] = users[mid + 1 + j]

        index_of_sub_array_one = 0
        index_of_sub_array_two = 0
        index_of_merged_array = left

        while index_of_sub_array_one < sub_array_one and index_of_sub_array_two < sub_array_two:
            if left_array[index_of_sub_array_one]['user_id'] <= right_array[index_of_sub_array_two]['user_id']:
                users[index_of_merged_array]['user_id'] = left_array[index_of_sub_array_one]['user_id']
                index_of_sub_array_one += 1
            else:
                users[index_of_merged_array]['user_id'] = right_array[index_of_sub_array_two]['user_id']
                index_of_sub_array_two += 1
            index_of_merged_array += 1

        # Copy the remaining elements of left[], if any
        while index_of_sub_array_one < sub_array_one:
            users[index_of_merged_array]['user_id'] = left_array[index_of_sub_array_one]['user_id']
            index_of_sub_array_one += 1
            index_of_merged_array += 1

        # Copy the remaining elements of right[], if any
        while index_of_sub_array_two < sub_array_two:
            users[index_of_merged_array]['user_id'] = right_array[index_of_sub_array_two]['user_id']
            index_of_sub_array_two += 1
            index_of_merged_array += 1

    @staticmethod
    def merge_sort(users, begin: int, end: int):
        if begin >= end:
            return

        mid = begin + (end - begin) // 2
        MergeSort.merge_sort(users, begin, mid)
        MergeSort.merge_sort(users, mid + 1, end)
        MergeSort.merge(users, begin, mid, end)


class QuickSort:
    @staticmethod
    def partition(items: List, low: int, high: int):

        pivot = items[high]

        i = low - 1

        for j in range(low, high):
            if items[j] <= pivot:
                i = i + 1

                (items[i], items[j]) = (items[j], items[i])

        (items[i + 1], items[high]) = (items[high], items[i + 1])

        return i + 1

    @staticmethod
    def quicksort(items: List, low: int, high: int):
        if low < high:
            pi = QuickSort.partition(items, low, high)

            QuickSort.quicksort(items, low, pi - 1)

            QuickSort.quicksort(items, pi + 1, high)


class QuickSortListDict:
    @staticmethod
    def partition(items: List[Dict], low: int, high: int, key1: str, key2: str):
        pivot = items[high]

        i = low - 1
        for j in range(low, high):
            if items[j][key1] < pivot[key1]:
                i += 1

                (items[i], items[j]) = (items[j], items[i])

            elif items[j][key1] == pivot[key1] and items[j][key2] >= pivot[key2]:
                i += 1

                (items[i], items[j]) = (items[j], items[i])

        (items[i + 1], items[high]) = (items[high], items[i + 1])

        return i + 1

    @staticmethod
    def quicksort(items: List[Dict], low: int, high: int, key1: str, key2: str):
        if low < high:
            pi = QuickSortListDict.partition(items, low, high, key1, key2)

            QuickSortListDict.quicksort(items, low, pi - 1, key1, key2)

            QuickSortListDict.quicksort(items, pi + 1, high, key1, key2)


if __name__ == '__main__':
    # users = [
    #     {
    #         "user_id": 1,
    #         "corrects": 10,
    #         "spend_time": 9
    #     },
    #     {
    #         "user_id": 2,
    #         "corrects": 12,
    #         "spend_time": 10
    #     },
    #     {
    #         "user_id": 3,
    #         "corrects": 9,
    #         "spend_time": 10
    #     },
    #     {
    #         "user_id": 4,
    #         "corrects": 7,
    #         "spend_time": 5
    #     },
    #     {
    #         "user_id": 5,
    #         "corrects": 10,
    #         "spend_time": 10
    #     },
    #     {
    #         "user_id": 6,
    #         "corrects": 12,
    #         "spend_time": 8
    #     },
    #     {
    #         "user_id": 7,
    #         "corrects": 12,
    #         "spend_time": 8
    #     }
    # ]
    #
    # pprint(users)
    # QuickSortListDict.quicksort(users, 0, len(users) - 1, "corrects", "spend_time")
    # print('\n')
    # users.reverse()
    # pprint(users)

    text = "<[>@@@@<]>"
    pattern = r"<([^<>]*?)>"
    replacement = r"(\1)"

    new_text = re.sub(pattern, replacement, text)
    print("Modified text:", new_text)
