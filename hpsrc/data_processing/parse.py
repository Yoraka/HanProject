import sys
import os
import glob
import tkinter as tk
from tkinter import filedialog

import re
import docx2txt
import json
import pickle
from collections import OrderedDict

from .. import indexing
'''
please open this file with utf-8 encoding
'''

global recursion_count
recursion_count = 0

class DictionaryEntry:
    def __init__(self, character, variants=None, synonyms=None, definitions=None, special_entries=None):
        self.character = character
        self.variants = variants or []
        self.synonyms = synonyms or []
        self.definitions = definitions or []
        self.special_entries = special_entries or []

    def to_dict(self):
        return {
            'character': self.character,
            'variants': self.variants,
            'synonyms': self.synonyms,
            'definitions': self.definitions,
            'special_entries': self.special_entries
        }

    def __repr__(self):
        return f"DictionaryEntry(character={self.character}, variants={self.variants}, synonyms={self.synonyms}, definitions={self.definitions}, special_entries={self.special_entries})"


def load_index_from_file(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)
    
def process_synonyms(meaning, recursion_count):
    # 检查递归深度
    if recursion_count >= 10:
        # 记录达到递归深度限制的同义词
        with open('loop_synonym.txt', 'a') as f:
            f.write( + '\n')
        return [], recursion_count

    pattern_optional_pinyin = r'通“([^”]*?)(?:\（([^）]*)\）)?”。([^。]*。)'

    # Use re.findall to accurately extract matches, now correctly handling optional pinyin
    all_matches_optional_pinyin = re.findall(pattern_optional_pinyin, meaning)

    # Prepare a more accurate result that includes the term, its pinyin (if provided), and the explanation
    results_with_optional_pinyin = [{"term": match[0], "pinyin": match[1] if match[1] else "None", "explanation": match[2]} for match in all_matches_optional_pinyin]

    ret_result = {}

    for result in results_with_optional_pinyin:
        # 检查每个结果的'explanation'字段是否存在特定字符
        if "《" in result['explanation'] or "》" in result['explanation'] or "*" in result['explanation']:
            # 如果存在，则将'explanation'设置为空字符串
            result['explanation'] = None

        ret_result = result['explanation']

    return ret_result, recursion_count


def meanings_process(meanings, index):
    # 通过一个全局计数来限制递归
    global recursion_count
    # 使用列表推导式找到只有制表符的元素
    tab_only_indices = [i for i, meaning in enumerate(meanings) if meaning.strip() == '']
    
    for i in reversed(tab_only_indices):
        meanings.pop(i)

    # 处理每个meaning里多余的换行符和制表符
    for i in range(len(meanings)):
        meanings[i] = meanings[i].replace('\n', '').replace('\t', '')

    # 按照要求，将meaning里第一个句号后的内容全部抛弃
    for i in range(len(meanings)):
        meanings[i] = meanings[i].split('。')[0]

    # 按照要求，暂时去除同“某字”的条目
    for i in reversed(range(len(meanings))):
        if re.search(r'同“(.*?)”', meanings[i]):
            meanings.pop(i)

    def extract_synonyms(meaning):
        # 匹配“通“某个汉字””格式的字符串
        pinyin = None
        match = re.search(r'通“([^”]+)”', meaning)
        if match:
            synonym_text = match.group(1)
            # 如果括号内是拼音，移除括号及拼音
            if re.search(r'（[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+）', synonym_text):
                pinyin_match = re.search(r'（([a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+）)', synonym_text)
                pinyin = pinyin_match.group(1).strip('（）')
                synonym_text = re.sub(r'（[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+）', '', synonym_text)
            # 清除可能存在的空格
            synonym_text = synonym_text.strip()
            # 提取括号内外的所有非空白字符
            synonyms = re.findall(r'[^\s（）]+', synonym_text)
            return synonyms, pinyin
        return [], None

    i = 0
    while i < len(meanings):
        synonyms, pinyin = extract_synonyms(meanings[i])  # 这个函数能提取同义词和拼音
        if synonyms:
            # 对于每个通，尝试找到并处理其解释
            for synonym in synonyms:
                valid_explanations, recursion_count = process_synonyms(meanings[i], recursion_count)
                if valid_explanations is not None:
                    meanings.extend(valid_explanations)
                else:
                    # 递归调用，直到找到没有同“某字”的条目
                    # 从索引中获取通“某字”的条目
                    entry_text = index.get(synonym)
                    if entry_text is not None:
                        if recursion_count < 10:
                            recursion_count += 1
                            entry = parse_dictionary_entry(entry_text, index)
                            recursion_count -= 1
                        else:
                            #print(f"Error: Recursion limit reached for synonym: {synonym}")
                            # 将该通字写入一个txt中
                            with open('.\output\checkpoint\loop_synonym.txt', 'a') as f:
                                f.write(synonym + '\n')
                            continue
                        if pinyin:
                            synonym_meanings = [m for d in entry.definitions if d['pinyin'] == pinyin for m in d['meanings']]
                        else:
                            synonym_meanings = [m for d in entry.definitions for m in d['meanings']]

                        meanings.extend(synonym_meanings)
                    else:
                        print(f"Error: Failed to find entry for synonym: {synonym}")
            meanings.pop(i)
        i += 1  # 移动到下一个meaning处理

def parse_multiple_entries(text, index):
    # 每个条目由两个井号（##）分隔
    entries_text = text.split('##')
    for i in range(len(entries_text)):
        entries_text[i] = entries_text[i][:-1]
    entries = []

    for entry_text in entries_text:
        # 确保条目文本不为空
        if entry_text.strip():
            entry = parse_dictionary_entry(entry_text, index)
            entries.append(entry)

    return entries


def parse_dictionary_entry(text, index):
    # 分割条目头和条目体 错误处理
    try:
        header, body = text.split('\n', 1)
    except ValueError:
        print(f"Error: Failed to split text: {text}")
    character = header.strip()
    entry = DictionaryEntry(character=character)

    # 根据条目的特征判断其类型并调用相应的解析函数
    if not re.search(r'（\d+）|(?<!“)\n\s+（[一二三四五六七八九十]+）(?!”)', body) and re.search(r'的(类推)?简化字', body) or '的讹字' in body:
        parse_variant(entry, body, index)
    elif not re.search(r'（\d+）|(?<!“)\n\s+（[一二三四五六七八九十]+）(?!”)', body) and '同“' in body:
        parse_synonym(entry, body, index)
    elif re.search(r'\s+《.+》|[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+', body):  # 假设所有正字条目都包含拼音和音韵书
        # 匹配包含 ㊀㊁㊂ 但不包含 （一）... 的
        if re.search(r'[㊀㊁㊂㊃㊄]+', body) and not re.search(r'(?<!“)\n\s+（[一二三四五六七八九十]+）(?!”)', body):
            parse_multi_old_rhyme(entry, body, index)
        if re.search(r'（\d+）', body) or re.search(r'(?<!“)\n\s+（[一二三四五六七八九十]+）(?!”)', body):  # 如果包含编号，可能是单音多义或多音多义
            if re.search(r'\n\s+（[一二三四五六七八九十]+）', body) or re.search(r'[①②③④⑤]', body):  # 如果包含数字或圆圈数字，是多音多义
                parse_multi_sound_multi_meaning(entry, body, index)
            else:
                parse_single_sound_multi_meaning(entry, body, index)
        else:
            parse_single_sound_single_meaning(entry, body, index)
    else:
        # 如果不符合以上任何一种模式，假设它是特殊字
        parse_special_entry(entry, body, index)

    # 对最终的每个definitions的meanings分别去重
    for definition in entry.definitions:
        #print("Before deduplication:", len(definition['meanings']))
        definition['meanings'] = list(OrderedDict.fromkeys(definition['meanings']))
        #print("After deduplication:", len(definition['meanings']))

    return entry

def parse_variant(entry, body, index):
    # 使用正则表达式来找到异体字的模式
    variant_matches = re.findall(r'(.+)的((类推)?简化字|讹字)', body)
    for match in variant_matches:
        entry.variants.append(match[0].strip())

def parse_synonym(entry, body, index):
    synonym_matches = re.findall(r'同“(.*?)”', body)
    for match in synonym_matches:
        entry.synonyms.append(match)
        # 按要求, 将同“某字”的definition直接写入到此entry的definition中
        entry_text = index.get(match)
        #print(type(entry_text))
        if print(type(entry_text)) is not None:
            entry.definitions = parse_dictionary_entry(entry_text, index).definitions
        else:
            # 放弃
            return

'''
有时候会有单音, 但多古音, 可以套函数调用 ㊀㊁㊂㊃㊄㊅㊆㊇㊈㊉
'''

def parse_multi_old_rhyme(entry, body, index, mode=0):
    #print(body)
    pinyin_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]\S*|\S*[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ](?=\s|$)', body)
    pinyin = pinyin_match.group(0) if pinyin_match else None

    # 按㊀㊁㊂切条目
    old_rhymes = re.split(r'\n[㊀㊁㊂㊃㊄]+', body, re.DOTALL)
    for old_rhyme in old_rhymes:
        if re.search(r'（\d+）', old_rhyme):
            # 然后按照之前单音多义的方式来解析
            parse_single_sound_multi_meaning(entry, old_rhyme, index, 2)
        else:
            parse_single_sound_single_meaning(entry, old_rhyme, index, 2)

    # 将拼音加入到每个定义中
    for definition in entry.definitions:
        definition['pinyin'] = pinyin
    

def parse_single_sound_single_meaning(entry, body, index, mode=0):
   
    pinyin_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]\S*|\S*[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ](?=\s|$)', body)
    pinyin = pinyin_match.group(0) if pinyin_match else None
    rhyme_match = None
    # 提取音韵
    if mode == 2:
        # 直接提取第一个回车前的字作为音韵书
        rhyme_book = body.split('\n')[0]
    else:
        rhyme_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+\s*《([^《\n]+)', body)
        rhyme_book = '《' + rhyme_match.group(1) if rhyme_match else None

    # 提取释义
    
    rhyme_end = rhyme_match.end(1) if rhyme_match else None
    if rhyme_end:
        meanings = body[rhyme_end:].split('\n')
    else:
        meanings = body.split('\n')[2:]

    meanings_process(meanings, index)

    if mode == 0:
        type = 'single_sound_single_meaning'
    elif mode == 1:
        type = 'multi_sound_single_meaning'
    elif mode == 2:
        type = 'single_sound_multi_rhyme_single_meaing'

    entry.definitions.append({
        'type': type,
        'pinyin': pinyin,
        'rhyme_book': rhyme_book,
        'meanings': meanings
    })

def parse_single_sound_multi_meaning(entry, body, index, mode=0):
    # 去除首个字符（如果第一个字符不是字母）
    body = body[2:] if not body[0].isalpha() else body
    
    # 提取拼音
    pinyin_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]\S*|\S*[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ](?=\s|$)', body)
    pinyin = pinyin_match.group(0) if pinyin_match else None

    # 提取音韵
    rhyme_match = None
    if mode == 2:
        # 直接提取第一个回车前的字作为音韵书
        rhyme_book = body.split('\n')[0]
    else:
        rhyme_match = re.search(r'[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+\s*《([^《\n]+)', body)
        # 会多去掉《, 所以要加上
        rhyme_book = '《' + rhyme_match.group(1) if rhyme_match else None

    # 提取释义
    # 也包括以⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵开头的释义
    meanings = re.findall(r'(?:\（\d+）|⑪|⑫|⑬|⑭|⑮|⑯|⑰|⑱|⑲|⑳|㉑|㉒|㉓|㉔|㉕|㉖|㉗|㉘|㉙|㉚|㉛|㉜|㉝|㉞|㉟|㊱|㊲|㊳|㊴|㊵)(.+?)(?=\n(?:\（\d+）|⑪|⑫|⑬|⑭|⑮|⑯|⑰|⑱|⑲|⑳|㉑|㉒|㉓|㉔|㉕|㉖|㉗|㉘|㉙|㉚|㉛|㉜|㉝|㉞|㉟|㊱|㊲|㊳|㊴|㊵)|\Z)', body, re.DOTALL)

    meanings_process(meanings, index)

    if mode == 0:
        type = 'single_sound_multi_meaning'
    elif mode == 1:
        type = 'multi_sound_multi_meaning'
    elif mode == 2:
        type = 'single_sound_multi_rhyme_multi_meaning'

    entry.definitions.append({
        'type': type,
        'pinyin': pinyin,
        'rhyme_book': rhyme_book,
        'meanings': meanings
    })

def parse_multi_sound_multi_meaning(entry, body, index):
    #把第一个（汉字数字）之前的片段都舍弃
    if not body[0] == '（':
        left_paren_index = body.find('（')
            # 使用切片获取左括号之后的内容
    if left_paren_index != -1:
        body = body[left_paren_index:]

    # 在前面加个回车符
    body = '\n' + body

    # 找到所有（汉字数字）这样的模式，按这个来切分多音，不取第一个
    # (一) ㊀ ①
    '''
    ⑪ ⑫ ⑬ ⑭ ⑮ ⑯ ⑰ ⑱ ⑲ ⑳
    ㉑ ㉒ ㉓ ㉔ ㉕ ㉖ ㉗ ㉘ ㉙ ㉚
    ㉛ ㉜ ㉝ ㉞ ㉟ ㊱ ㊲ ㊳ ㊴ ㊵
    ㊀ ㊁ ㊂ ㊃ ㊄ ㊅ ㊆ ㊇ ㊈ ㊉
    '''
    pronunciations = re.split(r'\n\（[一二三四五六七八九十]+）', body)
    pronunciations = pronunciations[1:]
    
    for pronunciation in pronunciations:
        if re.search(r'[㊀㊁㊂㊃㊄]+', pronunciation):
            parse_multi_old_rhyme(entry, pronunciation, index)
        elif re.search(r'（\d+）', pronunciation):
            # 然后按照之前单音多义的方式来解析每个多音
            parse_single_sound_multi_meaning(entry, pronunciation, index, 1)
        else:
            parse_single_sound_single_meaning(entry, pronunciation, index, 1)

def parse_special_entry(entry, body, index):
    #print(body)
    # 丢弃条目不录入
    meanings_process([body], index)
    entry.special_entries.append(body)

def print_ast(node, indent=0):
    # 打印当前节点的基本信息
    indent_str = ' ' * indent
    print(f"{indent_str}Character: {node.character}")

    if node.variants:
        print(f"{indent_str} Variants: {', '.join(node.variants)}")

    if node.synonyms:
        print(f"{indent_str} Synonyms: {', '.join(node.synonyms)}")

    # 打印每个定义
    for definition in node.definitions:
        print(f"{indent_str} Definition Type: {definition['type']}")
        print(f"{indent_str}  Pinyin: {definition['pinyin']}")
        if 'rhyme_book' in definition:
            print(f"{indent_str}  Rhyme Book: {definition['rhyme_book']}")
        if 'meanings' in definition:
            print(f"{indent_str}  Meanings: {', '.join(definition['meanings'])}")

    # 打印特殊条目
    for special_entry in node.special_entries:
        print(f"{indent_str} Special Entry: {special_entry}")


def save_as_json(entries, file_path, debug=False):
    # 打印解析后的所有条目
    if debug:
        for entry in entries:
            print_ast(entry)
            print("\n")  # 为了清晰可读，每个条目之间添加空行

    # 将所有条目转换为字典格式
    dict_entries = [entry.to_dict() for entry in entries]

    # 将字典列表转换为json字符串
    json_str = json.dumps(dict_entries, ensure_ascii=False, indent=4)

    # 将json字符串写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json_str)

# 读取本地文件
# text = docx2txt.process("tempA.docx")
# parsed_entries = parse_multiple_entries(text)

'''
没有必要用多线程
'''
def run(argv):
    print(recursion_count)
    # 加载索引
    index_file_path = '.\output\index\index_file.pkl'

    if not os.path.exists(index_file_path):
        print("Error: Index file not found.")
        choice = input('Do you wanna create index?(Y/N):')
        if choice == 'Y' or choice == 'y':
            if indexing.HansIndexCreator.run() == 1:
                print('Index created.')

            else:
                print('Index creation failed.')
                return 0

        else:
            print('Index creation aborted.')
            return 0

    print("Loading index...")

    index = load_index_from_file(index_file_path)

    print("Index loaded.")

    
    # 创建存储解析结果的文件夹
    if not os.path.exists('.\output\parsed_json'):
        os.makedirs('.\output\parsed_json')
    # 创建Tkinter窗口
    root = tk.Tk()
    root.withdraw()

    print("请选取文件, 如果一次处理多个文件请多选, 一般情况下请选择radicals_docx文件夹内的所有文件")

    if len(argv) > 1:
        print("Parsing...")
        # 获取文件路径
        file_path = argv[1]

        # 如果是文件夹，则获取文件夹路径下所有docx文件
        if os.path.isdir(file_path):
            docx_files = glob.glob(os.path.join(file_path, '*.docx'))
            for docx_file in docx_files:
                text = docx2txt.process(docx_file)
                parsed_entries = parse_multiple_entries(text, index)
                # 处理解析后的条目
                save_as_json(parsed_entries, os.path.join('.\output\parsed_json', os.path.basename(docx_file) + '.json'))
                
        # 如果是文件，则直接读取文件
        elif os.path.isfile(file_path):
            # 获取文件名
            docx_file_name, docx_file_ext = os.path.splitext(os.path.basename(file_path))
            text = docx2txt.process(file_path)
            parsed_entries = parse_multiple_entries(text, index)
            # 处理解析后的条目
            save_as_json(parsed_entries, os.path.join('.\output\parsed_json', docx_file_name + '.json'))

        else:
            print("Invalid file path.")
    else:
        root.deiconify()
        # 打开文件选取窗口
        file_path = filedialog.askopenfilenames(initialdir='./data', title='Select File', filetypes=[('Word Document', '*.docx'),('Any', '*.*')])
        root.withdraw()
        print("Parsing...")
        if file_path:
            for path in file_path:
                if os.path.isdir(path):
                    # 如果是文件夹，则获取文件夹路径下所有docx文件
                    docx_files = glob.glob(os.path.join(path, '*.docx'))
                    for docx_file in docx_files:
                        text = docx2txt.process(docx_file)
                        parsed_entries = parse_multiple_entries(text, index)
                        # 将解析后的条目存为json文件 json文件名为docx文件名 将json存放在本地parsed_json文件夹下
                        save_as_json(parsed_entries, os.path.join('.\output\parsed_json', os.path.basename(docx_file) + '.json'))

                elif os.path.isfile(path):
                    # 获取文件名
                    docx_file_name, docx_file_ext = os.path.splitext(os.path.basename(path))
                    # 如果是文件，则直接读取文件
                    text = docx2txt.process(path)
                    parsed_entries = parse_multiple_entries(text, index)
                    # 处理解析后的条目
                    save_as_json(parsed_entries, os.path.join('.\output\parsed_json', docx_file_name + '.json'))

    # 把synonym.txt中重复的字去掉，只保留一个
    # 结束

    with open('.\output\checkpoint\loop_synonym.txt', 'r') as f:
        data = f.read().split('\n')
        data = list(OrderedDict.fromkeys(data))
        with open('.\output\checkpoint\loop_synonym.txt', 'w') as f:
            for line in data:
                f.write(line + '\n')

    return 1

if __name__ == '__main__':
    run(sys.argv)