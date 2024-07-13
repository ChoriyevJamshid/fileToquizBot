import asyncio


async def get_txt_content(file_path):
    result = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as txt_file:
            for line in txt_file:
                line = line.strip()
                if line:
                    result.append(line)

    except FileNotFoundError:
        pass
    return result


