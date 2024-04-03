import json
import os

def extract_info(json_file, output_file, keywords):
    # 初始化提取结果
    extracted_info = []

    # 加载JSON数据
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取信息
    for entry in data:
        character = entry["character"]
        definitions = []
        for definition in entry["definitions"]:
            pinyin = definition.get("pinyin", "...")
            meanings = []
            # 检查meanings中的关键词
            for meaning in definition["meanings"]:
                if any(keyword in meaning for keyword in keywords):
                    meanings.append(meaning)
            if meanings:
                definitions.append({"pinyin": pinyin, "meanings": meanings})
        # 检查variants中的关键词
        for variant in entry["variants"]:
            if any(keyword in variant for keyword in keywords):
                definitions.append({"pinyin": "", "meanings": [variant]})
        if definitions:
            extracted_info.append({"character": character, "definitions": definitions})

    # 保存提取结果到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(extracted_info, file, ensure_ascii=False, indent=4)

def main():
    # 指定特定路径
    specific_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "output/_五大类25小类json")

    # 在特定路径中创建新文件夹
    new_folder_name = "tongjia_json"
    new_folder_path = os.path.join(specific_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # 设置关键词列表
    keywords = ["同“", "通“"]

    # 定义JSON文件和输出文件名的映射
    files_mapping = {
        'a9_⼈部.json': 'ren_通假字.json',
        'a30_⼝部.json': 'kou_通假字.json',
        'a61_⼼部.json': 'xin_通假字.json',
        'a76_⽋部.json': 'qian_通假字.json',
        'a149_⾔部.json': 'yan_通假字.json'
    }

    # 提取并保存信息
    for json_file, output_file_name in files_mapping.items():
        input_path = os.path.join('output', 'parsed_json', json_file)
        output_path = os.path.join(new_folder_path, output_file_name)
        extract_info(input_path, output_path, keywords)

    print(f"提取结果已保存到 {new_folder_path}")

if __name__ == '__main__':
    main()
