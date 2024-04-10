import json
import os
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import networkx as nx
import time
from matplotlib.font_manager import FontProperties
import matplotlib.path as mpath
import plotly.graph_objects as go

# 设置字体为支持中文的字体
font_path = "C:/Windows/Fonts/MSYH.TTC"
chinese_font = FontProperties(fname=font_path)

def reduce_dimensions(vectors, n_components=2, random_state=None,perplexity=100):
    tsne = TSNE(n_components=n_components, random_state=random_state,perplexity=perplexity)
    reduced_vectors = tsne.fit_transform(vectors)
    return reduced_vectors
import numpy as np

def load_vectors_and_meanings(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vectors = []
    display_texts = []
    for item in data:
        character = item['character']
        for definition in item['definitions']:
            meanings = definition['meanings']
            vec_strs = definition['vec']
            for meaning, vec_str in zip(meanings, vec_strs):
                display_text = f"{character}:{meaning}"
                display_texts.append(display_text)
                vec = [float(x) for x in vec_str.split(',')]
                vectors.append(vec)

    # Convert list of lists to a numpy array
    vectors = np.array(vectors)

    return vectors, display_texts

def plot_graph(vectors, labels, meanings, color_mapping):
    x, y = zip(*vectors)
    trace = go.Scatter(x=x, y=y, mode='markers', marker=dict(color=labels), text=meanings)

    layout = go.Layout(
        title="本义聚类图",
        hovermode='closest',
        xaxis=dict(title='x轴'),
        yaxis=dict(title='y轴'),
        showlegend=False,
        # 定义注释列表，以后将在这里添加颜色-部首注释
        annotations=[]
    )

    fig = go.Figure(data=[trace], layout=layout)

    # 自定义文本内容
    custom_texts = {
        'kou': '口部',
        'qian': '欠部',
        'ren': '人部',
        'xin': '心部',
        'yan': '言部'
    }
    # 添加每个颜色-部首配对作为注释
    annotations = []
    x_start =0.08  # 初始x位置
    x_offset = 0.05  # x位置的偏移量
    for part, color in color_mapping.items():
        # 使用自定义文本内容
        custom_text = custom_texts.get(part, part)  # 如果part不在custom_texts中，回退到使用part作为文本
        annotations.append(dict(
            text=f"<span style='color:{color};'>■</span> {custom_text}",  # 注释文本
            x=x_start, y=1.09,  # 注释的位置
            xref='paper', yref='paper',
            showarrow=False,
            font=dict(color=color,size=16), # 设置字体属性，包括颜色和大小
            align='left'
        ))
        x_start += x_offset  # 更新x位置以水平排列注释

    # 将注释添加到图表布局中
    fig.update_layout(annotations=annotations)

    output_dir = 'hpsrc/ForPicture/pic_html'
    os.makedirs(output_dir, exist_ok=True)  
    fig.write_html(f'{output_dir}/benyi.html') #生成html文件



    G = nx.Graph()
    for i, vector in enumerate(vectors):
        G.add_node(i, pos=vector, label=meanings[i], color=labels[i])

    pos = nx.get_node_attributes(G, 'pos')
    fig, ax = plt.subplots(figsize=(50, 50))
    nx.draw(G, pos, ax=ax, with_labels=False, node_color=[G.nodes[node]['color'] for node in G], node_size=10)

    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(node):
        x, y = pos[node]
        annot.xy = (x, y)
        text = G.nodes[node]['label']
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)
        annot.set_fontproperties(chinese_font)
        annot.set_position((0,10))  # 节点标签位置设置
        print(f'Annotation position: {annot.get_position()}, text: {text}')  # 用于检测bug

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            print('Hovering')  # 用于检测bug
            for node in G.nodes:
                x, y = pos[node]
                dist = np.sqrt((x - event.xdata)**2 + (y - event.ydata)**2)
                if dist < 1:  # 用于设置鼠标悬停处与节点相距位置
                    #设置太大的话无法精确显示每个节点的标签，所以最好设置为小于节点半径
                    update_annot(node)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()


    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.tight_layout()  # This will make the annotation box resize based on its content
    #plt.show()


def main():
    start_time = time.time()
    json_directory = 'output\\_五大类25小类json_with_vec\\benyi_json_with_vec'
    color_mapping = {
        'kou': 'red',
        'qian': 'green',
        'ren': 'blue',
        'xin': 'orange',
        'yan': 'purple'
    }

    all_vectors = []
    all_labels = []
    all_meanings = []

    for json_file in os.listdir(json_directory):
     if json_file.endswith('.json'):
        json_path = os.path.join(json_directory, json_file)
        prefix = json_file.split('_')[0]  # Extract prefix from filename
        color = color_mapping.get(prefix, 'gray')  # Default to gray if prefix not found in mapping
        vectors, meanings = load_vectors_and_meanings(json_path)
        all_vectors.append(vectors)
        all_labels.extend([color] * len(vectors))
        all_meanings.extend(meanings)

    print("完成向量加载。")
    load_end = time.time()
    print(f"加载向量耗时 {load_end - start_time} 秒。")

    print("正在降维...")
    reduction_start = time.time()
    #numpy的concatenate函数用于合并数组
    vectors = np.concatenate(all_vectors, axis=0)
    reduced_vectors = reduce_dimensions(vectors)
    reduction_end = time.time()
    print(f"降维耗时 {reduction_end - reduction_start} 秒。")

    print("正在绘制图形...")
    plot_start = time.time()
    plot_graph(reduced_vectors, all_labels, all_meanings,color_mapping)
    plot_end = time.time()
    print(f"绘图耗时 {plot_end - plot_start} 秒。")

    end_time = time.time()
    print(f"程序总运行时间： {end_time - start_time} 秒。")

if __name__ == '__main__':
    main()
