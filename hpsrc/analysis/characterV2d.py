from sklearn.decomposition import PCA
import re
import os
import glob
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
def run():
    font = {'family': 'Microsoft YaHei'}
    matplotlib.rc('font', **font, size=9)
    matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
    directory = './output/vec'

    # 使用PCA将数据降维到2D
    pca = PCA(n_components=2)
    # 获取所有包含 'meanings' 的 CSV 文件
    characters_files = glob.glob(os.path.join(directory, '*characters*.csv'))

    colors = ['red', 'green', 'blue', 'purple', 'orange', 'black']  # 6种颜色
    plt.figure(figsize=(10, 10))

    for idx, file in enumerate(characters_files):
        with open(file, 'r') as rfile:
            vectors_content = rfile.read()
            
        vector_regex = r"\[(.*?)\]"
        # 使用正则表达式提取所有向量
        vector_matches = re.findall(vector_regex, vectors_content, re.DOTALL)
        # 清理数据并转换为数字列表
        vectors = [[float(num) for num in vector.replace('\n', ' ').split()] for vector in vector_matches]

        vectors_2d = pca.fit_transform(vectors)
        # 检查向量的维度是否一致
        if not all(len(v) == len(vectors[0]) for v in vectors):
            raise ValueError("所有向量的维度必须相同。")
        
        # 绘制降维后的数据点
        plt.scatter(vectors_2d[:, 0], vectors_2d[:, 1], c=colors[idx % len(colors)], s=10 , label=f'{os.path.basename(file)}')

    plt.legend()
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.title('2D Projection of Vectors')
    plt.show()

if __name__ == '__main__':
    run()