import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
import umap
import hdbscan
import numpy as np
import os
import glob
import datamapplot
import re
import requests
import matplotlib
from fontTools import ttLib
from tempfile import NamedTemporaryFile

proxies = {
    "http": "http://127.0.0.1:10809",
}

def get_google_font(fontname):
    api_fontname = fontname.replace(' ', '+')
    api_response = resp = requests.get(f"https://fonts.googleapis.com/css?family={api_fontname}:black,bold,regular,light", verify=False)
    font_urls = re.findall(r'(https?://[^\)]+)', str(api_response.content))
    for font_url in font_urls:
        font_data = requests.get(font_url)
        f = NamedTemporaryFile(delete=False, suffix='.ttf')
        f.write(font_data.content)
        f.close()
        font = ttLib.TTFont(f.name)
        font_family_name = font['name'].getDebugName(1)
        matplotlib.font_manager.fontManager.addfont(f.name)
        print(f"Added new font as {font_family_name}")

get_google_font('Cinzel')

def convert_vector(vector):
    vector_regex = r"\[(.*?)\]"
    # 使用正则表达式提取所有向量
    vector_matches = re.findall(vector_regex, vector, re.DOTALL)
    # 清理数据并转换为数字列表
    vectors = [[float(num) for num in vector.replace('\n', ' ').split()] for vector in vector_matches]
    return vectors

print('begin')

# 设置文件夹路径
directory = './output/vec'
# 获取所有包含 'characters' 的 CSV 文件
characters_files = glob.glob(os.path.join(directory, '*characters*.csv'))
# 从csv文件构建data和radical_info
data = {}
radical_info = {}
for file in characters_files:
    df = pd.read_csv(file)
    for index, row in df.iterrows():
        character = row['character']
        # 获取向量的字符串表示
        vector_str = row['meanings_vec_average']
        # 使用 convert_vector 函数转换向量
        vector = convert_vector(vector_str)
        # 将转换后的向量添加到数据字典中
        data[character] = vector
        radical_info[character] = os.path.basename(file).split('_')[1][:1]

# 第一次聚类
clustersA = {}
clustersB = {}
for character, vector in data.items():
    radical = radical_info[character]
    if radical not in clustersB:
        clustersB[radical] = []
    clustersB[radical].append(character)

# 将character 和 vector 提取到结构化数据中
structured_data = []
for character, vector in data.items():
    structured_data.append({"character": character, "vector": vector})

#直接聚出50个类，不根据部首聚类
# preData是一个列表，包含所有的向量
# 设置DBSCAN的参数
"""epsilon = 0.5  # 邻域半径
min_samples = 600  # 最小点数

# 仅使用structured_data中的vector进行聚类, 聚类后要保留character到vector的映射
vectors = [item["vector"] for item in structured_data]
vectors = np.squeeze(vectors)

# 应用DBSCAN算法进行聚类
dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)
labels = dbscan.fit_predict(vectors)"""

# 准备数据
vectors = [item["vector"] for item in structured_data]
vectors = np.squeeze(vectors)

# t-SNE降维
tsne = TSNE(n_components=3, random_state=43)
reduced_vectors_tsne = tsne.fit_transform(vectors)

# DBSCAN聚类
dbscan = DBSCAN(eps=0.6, min_samples=30)
labels = dbscan.fit_predict(reduced_vectors_tsne)
#将聚类结果映射到character
for idx, label in enumerate(labels):
    character = list(data.keys())[idx]
    if label not in clustersA:
        clustersA[label] = []
    #将character与对应的vector添加到对应的聚类中
    clustersA[label].append({"character": character, "vector": structured_data[idx]['vector']})

def find_radical_by_character(character, clustersB):
    for radical, characters in clustersB.items():
        if character in characters:
            return radical
    return None  # 如果字符没有找到对应的部首，返回None

def find_group_by_character(character, clusters):
    for radical, members in clusters.items():
        if any(member['character'] == character for member in members):
            return radical
    return None

radical_counts = {}

# 对clustersA的key做个set
print(set(clustersA.keys()))

# 构建 new_clusters
new_clusters = {}
for cluster_id, members in clustersA.items():
    if cluster_id == -1:
        new_clusters['Unlabelled'] = members
        continue
    # 计算每个聚类中各个部首的数量
    radical_count = {}
    for member in members:
        character = member['character']
        radical = radical_info[character]
        if radical not in radical_count:
            radical_count[radical] = 0
        radical_count[radical] += 1
    # 确定主要部首
    # key名称为主要部首+count
    main_radical = str(max(radical_count, key=radical_count.get)).join(str(len(members)))
    if main_radical not in new_clusters:
        new_clusters[main_radical] = []
    new_clusters[main_radical].extend(members)

print(set(new_clusters.keys()))

# 计算每个聚类的中心点
centroids = {}
for radical, members in new_clusters.items():
    # 确保所有向量都是数值类型的列表或数组
    vectors = [np.array(member['vector']) for member in members]
    # 计算均值
    try:
        centroid = np.mean(vectors, axis=0)
        # 使用 squeeze 移除长度为1的维度
        centroid = np.squeeze(centroid)
        # 检查是否为一维数组
        if centroid.ndim != 1:
            raise ValueError(f"Centroid for radical {radical} is not a 1D array: {centroid}")
        centroids[radical] = centroid
    except:
        print(f"Error calculating centroid for radical {radical}, vectors: {vectors}")

# 对部首向量进行UMAP降维
#umap_reducer = umap.UMAP(n_neighbors=120, min_dist=0.3, n_components=2, random_state=24)
#reduced_centroids = umap_reducer.fit_transform(list(centroids.values()))

# 确保 data 字典中的每个值都是一个一维数组
for character in data:
    character_vector = [np.array(vector) if not isinstance(vector, np.ndarray) else vector for vector in data[character]]
    data[character] = np.squeeze(character_vector)

# 对所有汉字向量进行t-SNE降维
all_reduced_vectors = tsne.fit_transform(list(data.values()))

# 为每个字符生成原始标签
original_labels = []
for character in data.keys():
    radical = find_group_by_character(character, new_clusters)
    if radical is not None:
        label = radical
    else:
        label = 'Unlabelled'  # 特殊标签表示没有找到部首
    original_labels.append(label)

print(set(original_labels))

# 创建 data_map DataFrame
data_map = pd.DataFrame(all_reduced_vectors, columns=['x', 'y'])
data_map_labels = {}
data_map_labels['label'] = original_labels

# 生成标签
labels = [f"{radical}{len(new_clusters[radical])}" for radical in new_clusters.keys()]

# 第二次聚类，将降维后的数据聚类为10个类
#kmeans = KMeans(n_clusters=10)
#second_labels = kmeans.fit_predict(reduced_centroids)
#second_labels = [chr(65 + label) for label in second_labels]  # 将数字标签转换为字母标签

# 生成第二次聚类的标签,
# 将每个字符的原始标签映射到第二次聚类的标签，对齐
# 第二次聚类中，聚类内字符数量少于1550的聚类标记为Unlabelled
#data_map_labels['second_label'] = [second_labels[ord(radical) - 19968] if len(clustersA[radical]) >= 50 else 'Unlabelled' for radical in data_map_labels['label']]

data_map_array = data_map.to_numpy(dtype=np.float32)
# 检查data_map和data_map_labels的长度是否一致
if len(data_map_array) != len(data_map_labels['label']):
    raise ValueError("data_map and data_map_labels must have the same length.")

print('plotting')

#检查data_map_labels中是否有int
for label in data_map_labels['label']:
    if isinstance(label, int):
        print(label)

# 为所有标签做个set
print(set(data_map_labels['label']))

data_map_labels['label'] = [str(label) for label in data_map_labels['label']]

hover_text = data.keys()

# 绘制可交互的图表
plot = datamapplot.create_interactive_plot(
    data_map_array,
    data_map_labels['label'],
    #data_map_labels['second_label'],
    hover_text=hover_text,
    title='Example Data Map',
    sub_title='A data map of example data',
    noise_label='Unlabelled',
    font_family='Microsoft YaHei',
    point_radius_min_pixels=1,
    point_radius_max_pixels=4,
    point_line_width=0,
    cluster_boundary_polygons=True,
    cluster_boundary_line_width=6,
    darkmode=True,
)
print('show')
plot
print('saving')
plot.save("data_map_example.html")
