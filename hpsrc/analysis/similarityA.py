import re
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
def run():
    # 设置Matplotlib支持中文的字体
    # 微软雅黑
    font = {'family': 'Microsoft YaHei'}
    matplotlib.rc('font', **font, size=9)
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

    directory = './output/vec'

    # 获取所有包含 'meanings' 的 CSV 文件
    characters_files = glob.glob(os.path.join(directory, '*characters*.csv'))
    vector_means = []
    for idx, file in enumerate(characters_files):
        with open(file, 'r') as rfile:
            vectors_content = rfile.read()
            
        vector_regex = r"\[(.*?)\]"
        # 使用正则表达式提取所有向量
        vector_matches = re.findall(vector_regex, vectors_content, re.DOTALL)
        # 清理数据并转换为数字列表
        vectors = [[float(num) for num in vector.replace('\n', ' ').split()] for vector in vector_matches]

        # 检查向量的维度是否一致
        if not all(len(v) == len(vectors[0]) for v in vectors):
            raise ValueError("所有向量的维度必须相同。")
        
        # 计算向量的平均值
        vector_mean = [sum(vector) / len(vector) for vector in zip(*vectors)]
        vector_means.append(vector_mean)

    def cosine_similarity(vec1, vec2):
        """计算两个向量的余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a**2 for a in vec1) ** 0.5
        magnitude2 = sum(b**2 for b in vec2) ** 0.5
        if magnitude1 == 0 or magnitude2 == 0:
            # 避免除以零
            return 0
        return dot_product / (magnitude1 * magnitude2)
    # 基于一个平均向量算出与其他平均向量的相似度
    for idx, vector_mean in enumerate(vector_means):
        print(f'与 {os.path.basename(characters_files[idx])} 的相似度：')
        for idx2, vector_mean2 in enumerate(vector_means):
            if idx == idx2:
                continue
            similarity = cosine_similarity(vector_mean, vector_mean2)
            print(f'{os.path.basename(characters_files[idx2])}：{similarity:.2f}')
        print()
        # 保存到 output/similarity.txt
        """
        with open('./output/similarity.txt', 'a') as wfile:
            wfile.write(f'与 {os.path.basename(characters_files[idx])} 的相似度：\n')
            for idx2, vector_mean2 in enumerate(vector_means):
                if idx == idx2:
                    continue
                similarity = cosine_similarity(vector_mean, vector_mean2)
                wfile.write(f'{os.path.basename(characters_files[idx2])}：{similarity:.2f}\n')
            wfile.write('\n')"""

    # 继续之前的代码，添加绘制热图的部分

    # 首先计算所有平均向量之间的相似度
    similarity_matrix = []
    for vector_mean1 in vector_means:
        row = []
        for vector_mean2 in vector_means:
            similarity = cosine_similarity(vector_mean1, vector_mean2)
            row.append(similarity)
        similarity_matrix.append(row)

    # 将相似度矩阵转换为 DataFrame
    similarity_df = pd.DataFrame(similarity_matrix, index=[os.path.basename(file) for file in characters_files], columns=[os.path.basename(file) for file in characters_files])

    # 绘制热图
    # 图像缩小点，防止显示不全
    plt.figure(figsize=(10, 10))
    sns.heatmap(similarity_df, annot=False, cmap="YlGnBu")
    plt.title('部首字符向量平均值的相似度热图')
    plt.xticks([])
    plt.yticks([])
    plt.show()
    return
    import networkx as nx

    # 创建一个网络图对象
    G = nx.Graph()

    # 添加节点
    for file in characters_files:
        G.add_node(os.path.basename(file))

    # 添加边和权重（基于相似度的倒数）
    for i, vector_mean1 in enumerate(vector_means):
        for j, vector_mean2 in enumerate(vector_means):
            if i != j:
                similarity = cosine_similarity(vector_mean1, vector_mean2)
                # 使用相似度的倒数作为权重
                weight = 1 / similarity if similarity != 0 else 0
                G.add_edge(os.path.basename(characters_files[i]), os.path.basename(characters_files[j]), weight=weight)

    # 使用力导向布局
    pos = nx.spring_layout(G, k=0.15, iterations=20)

    # 绘制网络图
    edges = G.edges(data=True)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2500, edge_color=[data['weight'] for _, _, data in edges], width=3.0, edge_cmap=plt.cm.Blues)
    plt.title('部首字符向量网络图')
    plt.show()

if __name__ == '__main__':
    run()