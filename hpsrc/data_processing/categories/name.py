import json
import os

def extract_info(json_file, output_file, keywords, exclude_keywords, end_keywords):
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
            # 检查meanings中的关键词
            for meaning in definition["meanings"][1:]:
                if (any(keyword in meaning for keyword in keywords) or meaning.endswith(tuple(end_keywords))) and not any(exclude_keyword in meaning for exclude_keyword in exclude_keywords):
                    if pinyin not in pinyin_info:
                        pinyin_info[pinyin] = []
                    pinyin_info[pinyin].append(meaning)
                    has_valid_entry = True
            # 检查variants中的关键词
        for variant in entry["variants"]:
            if (any(keyword in variant for keyword in keywords) or variant.endswith(tuple(end_keywords))) and not any(exclude_keyword in variant for exclude_keyword in exclude_keywords):
                if pinyin not in pinyin_info:
                    pinyin_info[pinyin] = []
                pinyin_info[pinyin].append(variant)
                has_valid_entry = True
        if has_valid_entry:
            extracted_info[character] = pinyin_info

    # 保存提取结果到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        for character, pinyins in extracted_info.items():
            file.write(f"{character}:\n")
            for pinyin, meanings in pinyins.items():
                file.write(f"  {pinyin}: ")
                file.write(f"{meanings[0]}\n")
                for meaning in meanings[1:]:
                    file.write(f"      {meaning}\n")

def main():
    # 指定特定路径和其他参数
    specific_path = "output"
    new_folder_name = "_专用名词"
    new_folder_path = os.path.join(specific_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # 设置关键词列表
    end_keywords = []
    keywords = ["名"]
    exclude_keywords = ["得名", "名字", "名声", "闻名"]

    # 定义JSON文件和输出文件名的映射
    files_mapping = {
        'a9_⼈部.json': '_人_专用名词.txt',
        'a30_⼝部.json': '_口_专用名词.txt',
        'a61_⼼部.json': '_心_专用名词.txt',
        'a76_⽋部.json': '_欠_专用名词.txt',
        'a149_⾔部.json': '_言_专用名词.txt'
    }

    # 提取并保存信息
    for json_file, output_file_name in files_mapping.items():
        input_path = os.path.join('output', 'parsed_json', json_file)
        output_path = os.path.join(new_folder_path, output_file_name)
        extract_info(input_path, output_path, keywords, exclude_keywords, end_keywords)

    print(f"提取结果已保存到 {new_folder_path}")

if __name__ == '__main__':
    main()