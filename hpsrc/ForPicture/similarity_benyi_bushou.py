import csv
import json
import numpy as np
import os

def cosine_similarity(vec1, vec2):
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:  # 检查任一向量是否为零向量
        return 0  # 如果有一个是零向量，则返回0
    else:
        dot_product = np.dot(vec1, vec2)
        return dot_product / (norm_vec1 * norm_vec2)

# 加载5radicals.json中的部首向量
with open('output\\5radicals.json', 'r', encoding='utf-8') as file:
    radicals_vectors = json.load(file)

# 部首和文件名的映射
radical_files = {
    '口': 'kou_本义',
    '欠': 'qian_本义',
    '人': 'ren_本义',
    '心': 'xin_本义',
    '言': 'yan_本义'
}

# 基础目录
base_dir = 'output\_五大类25小类json_with_vec\\benyi_json_with_vec'
# 输出目录
output_dir = 'output/similarity'

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历每个部首及其对应的文件
for radical, filename in radical_files.items():
    radical_vec = np.array(radicals_vectors[radical])
    file_path = os.path.join(base_dir, f'{filename}.json')
    
    # 准备结果列表和相似度列表
    results = []
    similarities = []

    # 读取文件中的所有字及其向量
    with open(file_path, 'r', encoding='utf-8') as file:
        characters_data = json.load(file)

    for char_data in characters_data:
        character = char_data['character']
        for definition in char_data['definitions']:
            pinyin = definition['pinyin']
            # 检查vec字段是否存在并且不为空
            if 'vec' in definition and definition['vec']:
                vec_str = definition['vec'][0]  # 假设每个定义只有一个向量
                char_vec = np.array([float(x) for x in vec_str.split(',')])
                # 计算余弦相似度
                similarity = cosine_similarity(char_vec, radical_vec)
            else:
                similarity = 0  # vec不存在或为空时设置相似度为0

            results.append({'character': character, 'pinyin': pinyin, 'similarity': similarity})
            similarities.append(similarity)

    # 计算相似度的平均值
    avg_similarity = np.mean(similarities)

    # 按相似度降序排列结果
    sorted_results = sorted(results, key=lambda x: x['similarity'], reverse=True)

    # 将结果保存到新文件中
    output_file_path = os.path.join(output_dir, f'{filename}.csv')
    with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
        fieldnames = ['character', 'pinyin', 'similarity']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'character': '平均相似度', 'pinyin': '', 'similarity': avg_similarity})
        for result in sorted_results:
            writer.writerow(result)

    print(f"部首 '{radical}' 的相似度计算结果已保存到 {output_file_path}")

print("所有部首的相似度计算已完成。")
