import json
import os

# 读取停用词
stopwords_path = 'data/stopwords.txt'
with open(stopwords_path, 'r', encoding='utf-8') as file:
    stopwords = set(file.read().splitlines())

# 定义处理的文件列表
files = ['kou_本义', 'qian_本义','ren_本义','xin_本义','yan_本义']  # 请根据需要添加其他文件名
base_dir = 'output\_五大类25小类json_with_vec\\benyi_json_with_vec'

# 输出目录
output_dir = 'output/benyi_length'
# 创建输出目录如果它不存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历每个文件
for filename in files:
    file_path = os.path.join(base_dir, f'{filename}.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        characters_data = json.load(file)

    # 将结果保存到新文件中
    output_file_path = os.path.join(output_dir, f'{filename}_length.txt')
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # 遍历每个字符的数据
        for char_data in characters_data:
            character = char_data['character']
            
            # 遍历每个拼音的定义
            for definition in char_data['definitions']:
                pinyin = definition['pinyin']
                
                # 遍历每个意思并计算字数（去除停用词后）
                for meaning in definition['meanings']:
                    words = list(meaning)  # 将意思分割为单个字符
                    # 移除停用词
                    words_filtered = [word for word in words if word not in stopwords]
                    char_count = len(words_filtered)  # 计算剩余字符数量
                    
                    # 写入结果
                    output_file.write(f"{character}({pinyin}): {meaning}; 字数: {char_count}\n")

    print(f"部首 '{filename}' 的字数统计结果已保存到 {output_file_path}")

print("所有部首的字数统计已完成。")
