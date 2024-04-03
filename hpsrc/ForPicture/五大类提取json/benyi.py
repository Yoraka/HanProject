import json
import os

def extract_info(json_file, output_file):
    # 初始化提取结果
    extracted_info = []

    # 加载JSON数据
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取信息
    for entry in data:
        character = entry["character"]
        definitions = []
        if "definitions" in entry:
            for definition in entry["definitions"]:
                pinyin = definition.get("pinyin", "")
                if "meanings" in definition and definition["meanings"]:
                    meaning = definition["meanings"][0]
                    definitions.append({
                        "pinyin": pinyin, 
                        "meanings": [meaning]
                    })
        if definitions:
            extracted_info.append({
                "character": character, 
                "definitions": definitions
            })

    # 保存提取结果到新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(extracted_info, file, ensure_ascii=False, indent=4)




def main():
    # 指定特定路径和其他参数
    specific_path = "output/_五大类25小类json"
    new_folder_name = "benyi_json"
    new_folder_path = os.path.join(specific_path, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)

    # 定义JSON文件和输出文件名的映射
    files_mapping = {
        'a9_⼈部.json': 'ren_本义.json',
        'a30_⼝部.json': 'kou_本义.json',
        'a61_⼼部.json': 'xin_本义.json',
        'a76_⽋部.json': 'qian_本义.json',
        'a149_⾔部.json': 'yan_本义.json'
    }

    # 提取并保存信息
    for json_file, output_file_name in files_mapping.items():
        input_path = os.path.join('output', 'parsed_json', json_file)
        output_path = os.path.join(new_folder_path, output_file_name)
        extract_info(input_path, output_path)

    print(f"提取结果已保存到 {new_folder_path}")

if __name__ == '__main__':
    main()
