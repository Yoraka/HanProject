import os
import json
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.manifold import TSNE

def load_data(file_paths):
    """加载数据，并为每个释义生成向量"""
    data = []
    all_words = set()  # 用于收集所有的单词
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            for entry in json_data:
                if isinstance(entry, dict):
                    character = entry.get("character", "")  # 获取字典中的字符键值，如果不存在则使用空字符串
                    definitions = entry.get("definitions", [])
                    for definition in definitions:
                        if isinstance(definition, dict):
                            pinyin = definition.get("pinyin", "")
                            meanings = definition.get("meanings", [])
                            for meaning in meanings:
                                data.append((character, pinyin, meaning, file_path))
                                all_words.update(meaning.split())  # 更新单词集合
    feature_names = list(all_words)  # 将集合转换为列表
    return data, feature_names


def calculate_vectors(data, feature_names):
    """为每个释义计算向量"""
    vectors = []
    for meaning, _ in data:
        vector = np.zeros(len(feature_names))
        for word in meaning.split():
            if word in feature_names:
                vector[feature_names.index(word)] += 1
        vectors.append(vector)
    return np.array(vectors)

def reduce_dimensions(vectors, n_components=2, random_state=None):
    """使用TSNE降维"""
    tsne = TSNE(n_components=n_components, random_state=random_state)
    reduced_vectors = tsne.fit_transform(vectors)
    return reduced_vectors

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
        'output\_五大类25小类json\_本义json\_口_本义.json',
        'output\_五大类25小类json\_本义json\_欠_本义.json',
        'output\_五大类25小类json\_本义json\_人_本义.json',
        'output\_五大类25小类json\_本义json\_心_本义.json',
        'output\_五大类25小类json\_本义json\_言_本义.json'
    ]

    data, feature_names = load_data(file_paths)

    # 假设我们已经有了一个特征名称列表
    if not feature_names:
        feature_names = [...]  # 需要填充这个列表

    vectors = calculate_vectors(data, feature_names)
    reduced_vectors = reduce_dimensions(vectors)

    labels = [label for _, _, _, label in data]

    plot_graph(reduced_vectors, labels, file_paths)

if __name__ == '__main__':
    main()
