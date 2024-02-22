import json
import os

def extract_info(json_file, output_file):
    # 初始化提取结果
    extracted_info = {}

    # 加载JSON数据
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取信息
    for entry in data:
        character = entry["character"]
        has_valid_entry = False
        pinyin_info = {}
        for definition in entry["definitions"]:
            pinyin = definition.get("pinyin", "...")
            meaning = definition["meanings"][0] if definition["meanings"] else "..."
            if pinyin not in pinyin_info:
                pinyin_info[pinyin] = []
            pinyin_info[pinyin].append(meaning)
            has_valid_entry = True
        if has_valid_entry:
            extracted_info[character] = pinyin_info
        else:
            extracted_info[character] = {"...": ["..."]}

    # 保存提取结果到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        for character, pinyins in extracted_info.items():
            file.write(f"{character}:\n")
            for pinyin, meanings in pinyins.items():
                file.write(f"  {pinyin}: ")
                for i, meaning in enumerate(meanings):
                    if i == 0:
                        file.write(f"{meaning}\n")
                    else:
                        file.write(f"      {meaning}\n")

def main():
    # 指定特定路径和其他参数
    specific_path = "output"
    new_folder_name = "_本义"
    new_folder_path = os.path.join(specific_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # 定义JSON文件和输出文件名的映射
    files_mapping = {
        'a9_⼈部.json': '_人_本义.txt',
        'a30_⼝部.json': '_口_本义.txt',
        'a61_⼼部.json': '_心_本义.txt',
        'a76_⽋部.json': '_欠_本义.txt',
        'a149_⾔部.json': '_言_本义.txt'
    }

    # 提取并保存信息
    for json_file, output_file_name in files_mapping.items():
        input_path = os.path.join('output', 'parsed_json', json_file)
        output_path = os.path.join(new_folder_path, output_file_name)
        extract_info(input_path, output_path)

    print(f"提取结果已保存到 {new_folder_path}")

if __name__ == '__main__':
    main()
