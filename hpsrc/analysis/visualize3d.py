import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
def run():
    # 设置文件夹路径
    directory = './output/vec'

    # 初始化 PCA，将数据降维到三维
    model = PCA(n_components=3)

    # 获取所有包含 'meanings' 的 CSV 文件
    meanings_files = glob.glob(os.path.join(directory, '*meanings*.csv'))

    colors = ['red', 'green', 'blue', 'purple', 'orange']  # 五种颜色
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')  # 创建 3D 坐标轴

    for idx, file in enumerate(meanings_files):
        # 读取 CSV 文件
        df = pd.read_csv(file)
        
        # 将数据降维到三维
        reduced_data = model.fit_transform(df)

        # 绘制降维后的数据点
        ax.scatter(reduced_data[:, 0], reduced_data[:, 1], reduced_data[:, 2], c=colors[idx % len(colors)], label=f'{os.path.basename(file)}')

    ax.legend()
    ax.set_title('3D Visualization of Meanings Vectors')
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')
    ax.set_zlabel('Component 3')
    plt.show()
    input('Press Enter to continue...')

if __name__ == '__main__':
    run()