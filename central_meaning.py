import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取heart.json文件
with open('./parsed_json/heart.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    if not entry['definitions']:  # 检查definitions是否为空
        # 如果definitions为空，按照指定格式添加占位符
        formatted_output.append(f"{character}（...）: ...")
    else:
        for definition in entry['definitions']:
            pinyin = definition['pinyin']
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('heart_formatted_output.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取man.json文件
with open('./parsed_json/man.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    if not entry['definitions']:  # 检查definitions是否为空
        # 如果definitions为空，按照指定格式添加占位符
        formatted_output.append(f"{character}（...）: ...")
    else:
        for definition in entry['definitions']:
            pinyin = definition['pinyin']
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('man_formatted_output.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取mouth.json文件
with open('./parsed_json/mouth.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    if not entry['definitions']:  # 检查definitions是否为空
        # 如果definitions为空，按照指定格式添加占位符
        formatted_output.append(f"{character}（...）: ...")
    else:
        for definition in entry['definitions']:
            pinyin = definition['pinyin']
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('mouth_formatted_output.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取sound.json文件
with open('./parsed_json/sound.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    if not entry['definitions']:  # 检查definitions是否为空
        # 如果definitions为空，按照指定格式添加占位符
        formatted_output.append(f"{character}（...）: ...")
    else:
        for definition in entry['definitions']:
            pinyin = definition['pinyin']
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('sound_formatted_output.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取speak.json文件
with open('./parsed_json/speak.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    if not entry['definitions']:  # 检查definitions是否为空
        # 如果definitions为空，按照指定格式添加占位符
        formatted_output.append(f"{character}（...）: ...")
    else:
        for definition in entry['definitions']:
            pinyin = definition['pinyin']
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('speak_formatted_output.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')
