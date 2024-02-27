import json
import re

# 读取txt文件，并转换为json格式
def txt_to_json(txt_file, json_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 初始化json对象
    data = {'definitions': []}
    current_char = {}
    for line in lines:
        # 假设每行格式为 "character pinyin: meanings"
        # 分隔字符和拼音意义部分
        char_pinyin, meanings = line.strip().split(': ', 1)
        # 进一步分隔字符和拼音
        character, pinyin = re.split(r'\s+', char_pinyin, 1)
        
        # 如果是新字符，添加到definitions
        if current_char.get('character') != character:
            if current_char:
                # 如果current_char不为空，说明前一个字符处理完毕，添加到definitions
                data['definitions'].append(current_char)
            # 开始新字符的信息收集
            current_char = {'character': character, 'pinyins': []}

        # 拼音和意义分别处理
        meanings_list = meanings.split('; ')
        current_char['pinyins'].append({'pinyin': pinyin, 'meanings': meanings_list})

    # 不要忘记添加最后一个字符
    if current_char:
        data['definitions'].append(current_char)

    # 将json对象写入文件
    with open(json_file, 'w', encoding='utf-8') as jf:
        json.dump(data, jf, ensure_ascii=False, indent=4)

# 调用函数进行转换
txt_to_json('input.txt', 'output.json')
