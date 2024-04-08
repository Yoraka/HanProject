import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, euclidean_distances
from itertools import combinations
from matplotlib.font_manager import FontProperties

# 设置中文显示字体
font_path = "C:/Windows/Fonts/MSYH.TTC"
chinese_font = FontProperties(fname=font_path)

# 加载向量和释义
def load_vectors_and_meanings(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vectors = []
    meanings = []
    for item in data:
        character = item['character']
        for definition in item['definitions']:
            vec_strs = definition['vec']
            for vec_str in vec_strs:
                vec = [float(x) for x in vec_str.split(',')]
                vectors.append(vec)
                meanings.append(f"{character}: {definition['meanings'][0]}")
    return np.array(vectors), meanings

# 计算内聚力和离散度
def calculate_cohesion_separation(vectors):
    if len(vectors) <= 1:
        return 0, 0  # 如果只有一个向量，内聚力和离散度都为0

    distances = euclidean_distances(vectors)
    cohesion = np.sum(distances) / (2 * len(vectors))  # 平均内聚力
    separation = np.max(distances)  # 离散度为最大距离
    return cohesion, separation

# 绘制内聚力和离散度的柱状图
def plot_bar_chart(data, labels, title, ylabel):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(data)), data, color='skyblue')
    plt.title(title, fontsize=16, fontweight='bold', y=1.05, fontproperties=chinese_font)
    plt.ylabel(ylabel, fontproperties=chinese_font)
    plt.xticks(range(len(data)), labels, rotation=45, ha='right', fontproperties=chinese_font)

    # 在每个柱上显示具体数据
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, round(yval, 3), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

# 绘制部首组合的轮廓系数柱状图
def plot_silhouette_bar_chart(data, labels, title, ylabel):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(data)), data, color='skyblue')
    plt.title(title, fontsize=16, fontweight='bold', y=1.05, fontproperties=chinese_font)
    plt.ylabel(ylabel, fontproperties=chinese_font)
    plt.xticks(range(len(data)), labels, rotation=45, ha='right', fontproperties=chinese_font)

    # 在每个柱上显示具体数据，根据数据的正负调整标签的位置
    for bar in bars:
        yval = bar.get_height()
        offset = 0.0002 if yval >= 0 else -0.002  # 对负数数据进行向下调整
        plt.text(bar.get_x() + bar.get_width() / 2, yval + offset,
                 round(yval, 3), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

# 主程序
def main():
    json_directory = 'output/_五大类25小类json_with_vec/benyi_json_with_vec'
    radicals = ['kou', 'ren', 'xin', 'yan', 'qian']
    cohesion_data = []
    separation_data = []
    silhouette_data = []
    pairs = []

    # 计算部首组合的轮廓系数
    for radical1, radical2 in combinations(radicals, 2):
        vectors1, _ = load_vectors_and_meanings(os.path.join(json_directory, f'{radical1}_本义.json'))
        vectors2, _ = load_vectors_and_meanings(os.path.join(json_directory, f'{radical2}_本义.json'))
        vectors = np.concatenate((vectors1, vectors2))
        labels = np.array([0] * len(vectors1) + [1] * len(vectors2))
        silhouette = silhouette_score(vectors, labels)
        silhouette_data.append(silhouette)
        pairs.append(f'{radical1} & {radical2}')

    # 绘制部首组合的轮廓系数柱状图
    plot_silhouette_bar_chart(silhouette_data, pairs, '部首组合的轮廓系数', 'Silhouette系数')

    # 计算每个部首内聚力和离散度
    for radical in radicals:
        vectors, _ = load_vectors_and_meanings(os.path.join(json_directory, f'{radical}_本义.json'))
        cohesion, separation = calculate_cohesion_separation(vectors)
        cohesion_data.append(cohesion)
        separation_data.append(separation)

    # 绘制内聚力和离散度的柱状图
    plot_bar_chart(cohesion_data, radicals, '部首内聚力', '内聚力')
    plot_bar_chart(separation_data, radicals, '部首离散度', '离散度')

if __name__ == '__main__':
    main()
