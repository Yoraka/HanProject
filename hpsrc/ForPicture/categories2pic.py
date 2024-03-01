import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.manifold import TSNE
import matplotlib.colors as mcolors
from scipy.spatial.distance import cosine

def reduce_dimensions(vectors, method='tsne', n_components=2, random_state=None):
    if method == 'tsne':
        tsne = TSNE(n_components=n_components, random_state=random_state)
        reduced_vectors = tsne.fit_transform(vectors)
    else:
        raise ValueError("Unsupported dimensionality reduction method: {}".format(method))
    return reduced_vectors

def load_vectors_from_csv(file_paths):
    """加载向量数据从 CSV 文件"""
    data = []
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        vectors = df.to_numpy()
        data.append(vectors)
    return np.concatenate(data, axis=0)

def plot_graph(vectors, labels, file_paths, meanings):
    """绘制图形，鼠标悬停时显示节点标签"""
    # 为每个文件创建颜色映射
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    color_map = {file_path: color for file_path, color in zip(file_paths, colors)}

    # 根据其标签为每个向量创建颜色列表
    vector_colors = [color_map[label] for label in labels]
    # 调整颜色的透明度
    vector_colors = [(mcolors.to_rgba(color)[:3] + (0.25,)) for color in vector_colors]
    # 创建网络图
    G = nx.Graph()

    # 添加节点及其属性
    for i, vector in enumerate(vectors):
        G.add_node(i, pos=vector, label=meanings[i], color=vector_colors[i])

    # 绘制图形，不包含节点标签
    pos = nx.get_node_attributes(G, 'pos')
    fig, ax = plt.subplots()  # 创建一个新的图形窗口
    nx.draw(G, pos, ax=ax, with_labels=False, node_color=[data['color'] for _, data in G.nodes(data=True)], node_size=50)

    # 为每个节点添加交互式注释
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(node):
        x, y = pos[node]
        annot.xy = (x, y)
        text = f"{G.nodes[node]['label']}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for node in G.nodes:
                cont, ind = G.nodes[node]['label'], None
                if cont:
                    update_annot(node)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
        if vis:
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()


def main():
    base_directory = 'output/vec_for_pic'
    subdirectories = [os.path.join(base_directory, subdir) for subdir in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, subdir))]
    colors = ['red', 'green', 'blue', 'orange', 'purple']  # 为每个子文件夹分配一个颜色
    # 为每个子目录创建颜色映射
    color_map = {subdir: colors[idx] for idx, subdir in enumerate(subdirectories)}
    assert len(subdirectories) <= len(colors), "Number of subdirectories exceeds number of available colors."

    vectors = []
    labels = []
    meanings = []
    for idx, subdir in enumerate(subdirectories):
        file_paths = [os.path.join(subdir, file) for file in os.listdir(subdir) if file.endswith('.csv')]
        subdir_vectors = load_vectors_from_csv(file_paths)
        vectors.append(subdir_vectors)
        labels.extend([subdir] * len(subdir_vectors))  # Use subdir as the label instead of color
        meanings.extend([os.path.basename(file).replace('vec_for_pic.csv', '') for file in file_paths for _ in range(len(pd.read_csv(file)))])

    vectors = np.concatenate(vectors, axis=0)
    reduced_vectors = reduce_dimensions(vectors, method='tsne')

    plot_graph(reduced_vectors, labels, color_map, meanings)

if __name__ == '__main__':
    main()
