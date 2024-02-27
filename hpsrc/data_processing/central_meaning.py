import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取heart.json文件
with open('./output/parsed_json/a61_⼼部.json', 'r', encoding='utf-8') as file:
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
with open('_心_本义.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取man.json文件
with open('./output/parsed_json/a9_⼈部.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

for entry in json_data:
    character = entry['character']
    for definition in entry['definitions']:
        pinyin = definition['pinyin']
        if definition['meanings']:  # 检查meanings列表是否非空
            first_meaning = definition['meanings'][0]
            formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
        else:
            # 对于空的meanings列表，选择添加"..."
            formatted_output.append(f"{character}（{pinyin}）: ...")

# 将格式化的字符串写入文件
with open('_人_本义.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取mouth.json文件
with open('./output/parsed_json/a30_⼝部.json', 'r', encoding='utf-8') as file:
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
with open('_口_本义.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取sound.json文件
with open('./output/parsed_json/a76_⽋部.json', 'r', encoding='utf-8') as file:
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
with open('_欠_本义.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')

import json

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 打开并读取speak.json文件
with open('./output/parsed_json/a149_⾔部.json', 'r', encoding='utf-8') as file:
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
with open('_言_本义.txt', 'w', encoding='utf-8') as file:
    for line in formatted_output:
        file.write(line + '\n')
