import json
import os

# 初始化一个列表用于存储最终的格式化字符串
formatted_output = []

# 指定特定路径
specific_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "output")

# 在特定路径中创建新文件夹
new_folder_name = "_本义"
new_folder_path = os.path.join(specific_path, new_folder_name)
os.makedirs(new_folder_path, exist_ok=True)

# 定义一个函数来处理每个JSON文件
def process_json_file(input_file, output_file_name):
    with open(input_file, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    for entry in json_data:
        character = entry['character']
        for definition in entry['definitions']:
            pinyin = definition.get('pinyin', '...')
            if definition['meanings']:  # 检查meanings列表是否非空
                first_meaning = definition['meanings'][0]
                formatted_output.append(f"{character}（{pinyin}）: {first_meaning}")
            else:
                # 对于空的meanings列表，选择添加"..."
                formatted_output.append(f"{character}（{pinyin}）: ...")

    # 保存提取结果到新文件
    output_file = os.path.join(new_folder_path, output_file_name)
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in formatted_output:
            file.write(line + '\n')
    formatted_output.clear()  # 清空列表以便下一个文件的处理

# 处理每个JSON文件
process_json_file('output/parsed_json/a61_⼼部.json', '_心_本义.txt')
process_json_file('output/parsed_json/a9_⼈部.json', '_人_本义.txt')
process_json_file('output/parsed_json/a30_⼝部.json', '_口_本义.txt')
process_json_file('output/parsed_json/a76_⽋部.json', '_欠_本义.txt')
process_json_file('output/parsed_json/a149_⾔部.json', '_言_本义.txt')
