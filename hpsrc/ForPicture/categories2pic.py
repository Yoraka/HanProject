import os
import json
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial.distance import cosine

def load_vectors(file_paths):
    vectors = []
    labels = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                vectors.append(np.array(item['vector']))
                labels.append(file_path)
    return np.array(vectors), labels

def plot_graph(reduced_vectors, labels, file_paths):
    # 为每个文件创建一个颜色映射
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    color_map = {file_path: color for file_path, color in zip(file_paths, colors)}

    # 根据标签为每个向量创建颜色列表
    vector_colors = [color_map[label] for label in labels]

    # 调整颜色的透明度
    vector_colors = [(mcolors.to_rgba(color)[:3] + (0.5,)) for color in vector_colors]

    # 创建网络图
    G = nx.Graph()

    # 添加具有属性的节点
    for i, vector in enumerate(reduced_vectors):
        G.add_node(i, vector=vector, label=labels[i], color=vector_colors[i])

    # 计算向量之间的相似度并添加边
    for i in range(len(reduced_vectors)):
        for j in range(i + 1, len(reduced_vectors)):
            similarity = 1 - cosine(reduced_vectors[i], reduced_vectors[j])
            if similarity > 0.5:  # 可以调整这个阈值来控制添加边的密度
                G.add_edge(i, j, weight=similarity)

    # 使用相似度作为弹簧布局的权重
    pos = nx.spring_layout(G, weight='weight', iterations=50, pos=None,
                           dim=2, seed=None, k=None, scale=1)

    # 绘制图形，边颜色设置为透明
    nx.draw(G, pos, with_labels=False, node_color=[data['color'] for _, data in G.nodes(data=True)],
            node_size=50, edge_color="none")
    plt.show()

def main():
    file_paths = [
        'hpsrc\ForPicture\五大类绘图\五大类json\\benyi.json',
        'hpsrc\ForPicture\五大类绘图\五大类json\\cixing.json',
        'hpsrc\ForPicture\五大类绘图\五大类json\\mingcheng.json',
        'hpsrc\ForPicture\五大类绘图\五大类json\\tongjaizi.json',
        'hpsrc\ForPicture\五大类绘图\五大类json\\yinshenyi.json'
    ]

    vectors, labels = load_vectors(file_paths)
    reduced_vectors = vectors[:, :2]  # 假设向量已经是降维后的

    plot_graph(reduced_vectors, labels, file_paths)

if __name__ == '__main__':
    main()
