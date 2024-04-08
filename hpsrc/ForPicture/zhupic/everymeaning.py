import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, euclidean_distances
from matplotlib.font_manager import FontProperties
from sklearn.metrics import silhouette_samples

# 设置中文显示字体
font_path = "C:/Windows/Fonts/MSYH.TTC"  # 确保这个路径在你的机器上是正确的
chinese_font = FontProperties(fname=font_path)

#计算两两聚类的余弦相似度
def cosine_similarity(vecA, vecB):
    return np.dot(vecA, vecB) / (np.linalg.norm(vecA) * np.linalg.norm(vecB))

def calculate_and_plot_cosine_similarities(centers, prefixes):
    similarities = []
    labels = []
    
    for i in range(len(centers)):
        for j in range(i+1, len(centers)):
            similarity = cosine_similarity(centers[i], centers[j])
            similarities.append(similarity)
            labels.append(f'{prefixes[i]}-{prefixes[j]}')
    
    plot_bar_chart(similarities, labels, '两两聚类的余弦相似度', '余弦相似度')

#计算两两聚类间的jaccard相似度
def jaccard_similarity(vec1, vec2):
    set1 = set(tuple(row) for row in map(tuple, vec1))
    set2 = set(tuple(row) for row in map(tuple, vec2))
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def calculate_and_plot_jaccard_similarities(vectors_list, prefixes):
    similarities = []
    labels = []
    
    for i in range(len(vectors_list)):
        for j in range(i+1, len(vectors_list)):
            similarity = jaccard_similarity(vectors_list[i], vectors_list[j])
            similarities.append(similarity)
            labels.append(f'{prefixes[i]}-{prefixes[j]}')
    
    plot_bar_chart(similarities, labels, '两两聚类的Jaccard相似度', 'Jaccard相似度')


def load_vectors_and_meanings(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vectors = []
    for item in data:
        for definition in item['definitions']:
            vec_strs = definition['vec']
            for vec_str in vec_strs:
                vec = [float(x) for x in vec_str.split(',')]
                vectors.append(vec)
    return np.array(vectors)

# 计算内聚力和离散度
def calculate_cohesion_separation(vectors):
    if len(vectors) <= 1:
        return 0, 0  # 如果只有一个向量，内聚力和离散度都为0

    distances = euclidean_distances(vectors)
    cohesion = np.sum(distances) / (2 * len(vectors))  # 平均内聚力
    separation = np.max(distances)  # 离散度为最大距离
    return cohesion, separation

# 绘制柱状图
def plot_bar_chart(data, labels, title, ylabel):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(data)), data, color='skyblue')
    plt.title(title, fontsize=16, fontweight='bold', y=1.05, fontproperties=chinese_font)
    plt.ylabel(ylabel, fontproperties=chinese_font)
    plt.xticks(range(len(data)), labels, rotation=45, ha='right', fontproperties=chinese_font)

    # 在每个柱上显示具体数据
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 3), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def calculate_dbi(all_vectors):
    # 计算每个聚类的中心
    centers = [np.mean(vectors, axis=0) for vectors in all_vectors]

    # 计算每个聚类的平均距离 sigma
    sigmas = []
    for i, vectors in enumerate(all_vectors):
        distances = np.linalg.norm(vectors - centers[i], axis=1)  # 计算每个点到中心的距离
        sigma = np.mean(distances)
        sigmas.append(sigma)

    # 计算 DBI
    dbi_sum = 0
    for i in range(len(all_vectors)):
        max_ratio = 0
        for j in range(len(all_vectors)):
            if i != j:
                d_cent = np.linalg.norm(centers[i] - centers[j])  # 聚类中心之间的距离
                ratio = (sigmas[i] + sigmas[j]) / d_cent
                if ratio > max_ratio:
                    max_ratio = ratio
        dbi_sum += max_ratio

    dbi = dbi_sum / len(all_vectors)
    return dbi

# 主程序
def main():
    root_directory = 'output/_五大类25小类json_with_vec'
    prefixes = ['kou', 'yan', 'ren', 'qian', 'xin']
    cohesion_data = []
    separation_data = []
    silhouette_data = []

    all_vectors = []
    for prefix in prefixes:
        prefix_vectors = []
        for subdir in os.listdir(root_directory):
            subdir_path = os.path.join(root_directory, subdir)
            if os.path.isdir(subdir_path):
                for filename in os.listdir(subdir_path):
                    if filename.startswith(prefix):
                        json_path = os.path.join(subdir_path, filename)
                        vectors = load_vectors_and_meanings(json_path)
                        prefix_vectors.extend(vectors)
        if prefix_vectors:
            all_vectors.append(np.vstack(prefix_vectors))
    
    # 计算 DBI
    dbi = calculate_dbi(all_vectors)
    print(f"Davies-Bouldin Index: {dbi}")

    all_vectors = []
    for prefix in prefixes:
        prefix_vectors = []
        for subdir in os.listdir(root_directory):
            subdir_path = os.path.join(root_directory, subdir)
            if os.path.isdir(subdir_path):
                for filename in os.listdir(subdir_path):
                    if filename.startswith(prefix):
                        json_path = os.path.join(subdir_path, filename)
                        vectors = load_vectors_and_meanings(json_path)
                        prefix_vectors.extend(vectors)
        if prefix_vectors:
            all_vectors.append(np.vstack(prefix_vectors))

    # 计算聚类中心
    centers = [np.mean(vectors, axis=0) for vectors in all_vectors]
    
    # 计算两两聚类的余弦相似度并绘制柱状图
    calculate_and_plot_cosine_similarities(centers, prefixes)

    # 计算两两聚类的Jaccard相似度并绘制柱状图
    calculate_and_plot_jaccard_similarities(all_vectors, prefixes)

    # 计算每个聚类内部的内聚力和离散度
    for vectors in all_vectors:
            cohesion, separation = calculate_cohesion_separation(vectors)
            cohesion_data.append(cohesion)
            separation_data.append(separation)


        # 绘制内聚力和离散度的柱状图
    plot_bar_chart(cohesion_data, prefixes, '聚类内部的内聚力', '内聚力')
    plot_bar_chart(separation_data, prefixes, '聚类内部的离散度', '离散度')

if __name__ == '__main__':
    main()
