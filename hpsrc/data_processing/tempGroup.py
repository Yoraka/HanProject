import os
import glob
import pandas as pd
from sklearn.cluster import KMeans
import re

# 获取五个部首的meanings.csv文件
# 五个部首以a9, a30, a61, a76, a149开头
directory = './output/vec'
characters_files = glob.glob(os.path.join(directory, '*characters*.csv'))
# 筛出5个部首的文件
characters_files = [file for file in characters_files if os.path.basename(file).split('_')[0] in ['a9', 'a30', 'a61', 'a76', 'a149', '88']]
all_centroids = []
labels = {}
# 读取所有文件并进行聚类
# 聚类数量20
n_clusters = 10

for file in characters_files:
    with open(file, 'r') as f:
        vectors_content = f.read()
    # 读取CSV文件
    df = pd.read_csv(file)
    # 提取向量列
    vector_regex = r"\[(.*?)\]"
    # 使用正则表达式提取所有向量
    vector_matches = re.findall(vector_regex, vectors_content, re.DOTALL)
    # 清理数据并转换为数字列表
    vectors = [[float(num) for num in vector.replace('\n', ' ').split()] for vector in vector_matches]
    # 进行KMeans聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(vectors)
    # 将聚类中心添加到列表中
    all_centroids.append(kmeans.cluster_centers_)
    # 为每个字符分配聚类标签
    labels[os.path.basename(file)] = kmeans.labels_

# 将聚类中心转换为DataFrame
centroids_df = pd.DataFrame(all_centroids[0])
for i in range(1, len(all_centroids)):
    centroids_df = pd.concat([centroids_df, pd.DataFrame(all_centroids[i])])

# 重置索引
centroids_df.reset_index(drop=True, inplace=True)

if not os.path.exists('./output/clusters'):
    os.makedirs('./output/clusters')

# 保存聚类中心到CSV文件
centroids_df.to_csv('./output/clusters/centroids.csv', index=False)

# 保存每个字符的聚类标签到CSV文件
for file, label in labels.items():
    label_df = pd.DataFrame(label, columns=['cluster_label'])
    label_df.to_csv(f'./output/clusters/labels_{file}', index=False)