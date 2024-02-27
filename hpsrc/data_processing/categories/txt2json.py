import json

def parse_line(line):
    parts = line.split('（')
    character = parts[0]
    pinyin = parts[1].split('）')[0] if '）' in parts[1] else ""
    meanings = parts[1].split('）')[1].strip(': ').split('。')[0]
    if '“' in meanings and '”' in meanings:
        meanings = meanings.split('“')[1].rstrip('”')
    return character, pinyin, meanings


def convert_txt_to_json(input_file, output_file):
    results = []

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            character, pinyin, meanings = parse_line(line.strip())
            result = {
                "character": character,
                "definitions": [
                    {
                        "pinyin": pinyin,
                        "meanings": [meanings]
                    }
                ]
            }
            results.append(result)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

def main():
    input_file = '.\output\_五大类txt\_通假字\_心_通假字.txt'
    output_file = '_心_通假字.json'
    convert_txt_to_json(input_file, output_file)
    print(f"转换完成，结果已保存到 {output_file}")

if __name__ == '__main__':
    main()
