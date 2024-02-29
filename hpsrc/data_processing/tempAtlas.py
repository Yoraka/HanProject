import os
import json
def remove_stopwords_from_string(input_str, stopwords):
    # 遍历字符串中的每个字符
    cleaned_str = ''.join(char for char in input_str if char not in stopwords)
    return cleaned_str
json_files = [os.path.join(root, file) for root, dirs, files in os.walk("./output/parsed_json") for file in files if file.endswith(".json")]
print(len(json_files))
all_characters = []
for json_file in json_files:
    #if 'a9' or 'a61' or 'a30' or 'a76' or 'a149' in os.path.basename(json_file):
    if 'a9' in os.path.basename(json_file) or 'a30' in os.path.basename(json_file) or 'a61' in os.path.basename(json_file) or 'a76' in os.path.basename(json_file) or 'a149' in os.path.basename(json_file):
        print(f'Processing {json_file}')
        with open(json_file, 'r') as file:
            data = json.load(file)
            for entry in data:
                character = entry['character']
                definitions = entry.get('definitions', [])
                if len(definitions) != 0:
                    for definition in definitions:
                        meanings = definition.get('meanings', [])
                        if len(meanings) != 0:
                            for meaning in meanings:
                                all_characters.append({'character': character, 'meanings': meaning})

with open('testmeaning.json', 'w', encoding='utf-8') as file:
    json.dump(all_characters, file, ensure_ascii=False, indent=4)
    print(f'Output to testmeaning.json')
# Path: hpsrc/data_processing/json2vec.py