import os
import json
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.manifold import MDS
from scipy.spatial.distance import cosine
from sklearn.manifold import TSNE

def reduce_dimensions(vectors, method='tsne', n_components=2, random_state=None):
    if method == 'tsne':
        tsne = TSNE(n_components=n_components, random_state=random_state)
        reduced_vectors = tsne.fit_transform(vectors)
    else:
        raise ValueError("Unsupported dimensionality reduction method: {}".format(method))
    return reduced_vectors

def load_vectors(file_path):
    """加载向量数据"""
    with np.load(file_path, allow_pickle=True) as data:
        vectors = data['vectors']
        feature_names = data['feature_names']
    return vectors, feature_names

def load_data(file_paths):
    """加载数据"""
    data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            for entry in json_data:
                for definition in entry["definitions"]:
                    for meaning in definition["meanings"]:
                        data.append(meaning)
    return data

def calculate_similarity_matrix(vectors):
    """计算相似度矩阵"""
    n = len(vectors)
    similarity_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            similarity = 1 - cosine(vectors[i], vectors[j])
            similarity_matrix[i, j] = similarity_matrix[j, i] = similarity
    return similarity_matrix

def plot_graph(vectors, labels, file_paths):
    """绘制图形，不包含边"""
    # 为每个文件创建颜色映射
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    color_map = {file_path: color for file_path, color in zip(file_paths, colors)}

    # 根据其标签为每个向量创建颜色列表
    vector_colors = [color_map[label] for label in labels]

    # 调整颜色的透明度
    vector_colors = [(mcolors.to_rgba(color)[:3] + (0.5,)) for color in vector_colors]

    # 创建网络图
    G = nx.Graph()

    # 添加节点及其属性
    for i, vector in enumerate(vectors):
        G.add_node(i, pos=vector, label=labels[i], color=vector_colors[i])

    # 不绘制边地绘制图形
    nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=False, node_color=[data['color'] for _, data in G.nodes(data=True)], node_size=50)
    plt.show()

def main():
    file_paths = [
        'output/parsed_json/a9_⼈部.json',
        'output/parsed_json/a30_⼝部.json',
        'output/parsed_json/a61_⼼部.json',
        'output/parsed_json/a76_⽋部.json',
        'output/parsed_json/a149_⾔部.json'
    ]

    vectors, feature_names = load_vectors('output/vectors/vector_data.npz')
    reduced_vectors = reduce_dimensions(vectors, method='tsne')

    # 创建每个向量的标签，基于它来自的文件
    labels = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            for entry in json_data:
                for definition in entry["definitions"]:
                    count = len(definition['meanings'])
                    labels.extend([file_path] * count)

    plot_graph(reduced_vectors, labels, file_paths)

if __name__ == '__main__':
    main()
