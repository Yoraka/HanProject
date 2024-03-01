import matplotlib.pyplot as plt
import networkx as nx
import os
import glob
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

def run():
    # 定义五个特定部首的颜色
    special_radicals_colors = {
        'a9': 'red',
        'a30': 'green',
        'a61': 'yellow',
        'a76': 'purple',
        'a149': 'orange'
    }
    # 设置文件夹路径
    directory = './output/vec'
    
    # 初始化网络图
    G = nx.Graph()

    # 获取所有包含 'meanings' 的 CSV 文件
    meanings_files = glob.glob(os.path.join(directory, '*meanings*.csv'))

    # 用于存储所有向量和节点信息的列表
    all_centroids = []
    labels = {}  # 存储节点标签

    # 读取所有文件并进行聚类
    n_clusters = 1  # 每个文件中的聚类数量
    for idx, file in enumerate(meanings_files):
        df = pd.read_csv(file)
        kmeans = KMeans(n_clusters=n_clusters, n_init=3).fit(df.values)
        centroids = kmeans.cluster_centers_

        radical_name = os.path.basename(file).split('_')[1][:1]
        kx_idx = os.path.basename(file).split('_')[0]

        for centroid_index, centroid in enumerate(centroids):
            node_name = f"{kx_idx}_cluster_{centroid_index}"
            if kx_idx in special_radicals_colors:
                G.add_node(node_name, style='filled', fillcolor='white', edgecolor=special_radicals_colors[kx_idx])
            else:
                G.add_node(node_name, style='filled', fillcolor='white', edgecolor='blue')
            all_centroids.append(centroid)
            labels[node_name] = f"{radical_name}"  # 给每3个点一个共同的标签

    print('log1')

    # 计算所有聚类之间的余弦相似度
    similarity_matrix = cosine_similarity(all_centroids)

    print('log2')

    edges, weights = [], []
    # 假设 all_centroids 代表所有簇的中心点
    # similarity_matrix 是一个二维数组，表示每对簇之间的相似度

    for i in range(len(all_centroids)):
        max_similarity = 0
        max_j = -1

        # 寻找与簇i最相似的簇j
        for j in range(len(all_centroids)):
            if i != j and similarity_matrix[i][j] > max_similarity:
                max_similarity = similarity_matrix[i][j]
                max_j = j

        # 如果找到了具有较高相似度的簇，则添加这条边
        if max_similarity > 0:
            node_i = list(labels.keys())[i]
            node_j = list(labels.keys())[max_j]
            G.add_edge(node_i, node_j)
            edges.append((node_i, node_j))
            weights.append((1 / (1 - max_similarity) if max_similarity != 1 else 0))


    print('log3')

    # 使用力导向布局
    # k=0.25, i=150
    pos = nx.spring_layout(G, k=0.1, iterations=2)

    nx.draw_networkx_nodes(G, pos, node_size=200, node_color=[G.nodes[n]['fillcolor'] for n in G.nodes()], edgecolors=[G.nodes[n]['edgecolor'] for n in G.nodes()])

    print('log4')

    # 标签
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_family='Microsoft YaHei')
    # 边
    # 根据权重选择颜色, weights 现在是1 / (1 - similarity_matrix[i][j]),要适当处理使得颜色不会太深
    weights = []
    for weight in weights:
        if weight > 0.9:
            weights.append(weight / max(weights) * 0.5)
        else:
            weights.append(0)
    
    print('log5')

    for edge, weight in zip(edges, weights):
        if weight == 0:
            edges.remove(edge)
            weights.remove(weight)

    nx.draw_networkx_edges(G, pos, edgelist=edges, width=weights, edge_color=weights, edge_cmap=plt.cm.Blues)

    print('log6')

    # 显示图表
    plt.title('Meanings Vectors Network Graph')
    plt.axis('off')  # 关闭坐标轴
    plt.show()
    
run()
