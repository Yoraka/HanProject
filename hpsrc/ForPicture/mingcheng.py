import json
import os

def extract_info(json_file, output_file, keywords, exclude_keywords, end_keywords):
    # 初始化提取结果
    extracted_info = []

    # 加载JSON数据
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取信息
    for entry in data:
        character = entry["character"]
        has_valid_entry = False
        definitions = []
        for definition in entry["definitions"]:
            pinyin = definition.get("pinyin", "...")
            meanings = []
            # 检查meanings中的关键词
            for meaning in definition["meanings"][1:]:
                if (any(keyword in meaning for keyword in keywords) or meaning.endswith(tuple(end_keywords))) and not any(exclude_keyword in meaning for exclude_keyword in exclude_keywords):
                    meanings.append(meaning)
                    has_valid_entry = True
            if meanings:
                definitions.append({"pinyin": pinyin, "meanings": meanings})
        if has_valid_entry:
            extracted_info.append({"character": character, "definitions": definitions})

    # 保存提取结果到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(extracted_info, file, ensure_ascii=False, indent=4)

def main():
    # 指定特定路径和其他参数
    specific_path = "output/_五大类json"
    new_folder_name = "_专用名词json"
    new_folder_path = os.path.join(specific_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # 设置关键词列表
    end_keywords = []
    keywords = ["名","用语","术语","佛家语","梵语","谚语","客套语"]
    exclude_keywords = ["得名", "名字", "名声", "闻名"]

    # 定义JSON文件和输出文件名的映射
    files_mapping = {
        'a9_⼈部.json': '_人_专用名词.json',
        'a30_⼝部.json': '_口_专用名词.json',
        'a61_⼼部.json': '_心_专用名词.json',
        'a76_⽋部.json': '_欠_专用名词.json',
        'a149_⾔部.json': '_言_专用名词.json'
    }

    # 提取并保存信息
    for json_file, output_file_name in files_mapping.items():
        input_path = os.path.join('output', 'parsed_json', json_file)
        output_path = os.path.join(new_folder_path, output_file_name)
        extract_info(input_path, output_path, keywords, exclude_keywords, end_keywords)

    print(f"提取结果已保存到 {new_folder_path}")

if __name__ == '__main__':
    main()
