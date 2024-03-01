import json
import os
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import networkx as nx
import time
from matplotlib.font_manager import FontProperties

# 设置字体为支持中文的字体
font_path = "C:/Windows/Fonts/MSYH.TTC"
chinese_font = FontProperties(fname=font_path)

def reduce_dimensions(vectors, n_components=2, random_state=None):
    tsne = TSNE(n_components=n_components, random_state=random_state)
    reduced_vectors = tsne.fit_transform(vectors)
    return reduced_vectors

def load_vectors_and_meanings(json_file):
    vectors = []
    meanings = []
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for entry in data:
            for definition in entry['definitions']:
                for meaning, vec in zip(definition['meanings'], definition['vec']):
                    vectors.append(np.array(vec.split(','), dtype=float))
                    meanings.append(f"{entry['character']}: {meaning}")
    return np.array(vectors), meanings



def plot_graph(vectors, labels, meanings):
    G = nx.Graph()
    for i, vector in enumerate(vectors):
        G.add_node(i, pos=vector, label=meanings[i], color=labels[i])

    pos = nx.get_node_attributes(G, 'pos')
    fig, ax = plt.subplots()
    nx.draw(G, pos, ax=ax, with_labels=False, node_color=[G.nodes[node]['color'] for node in G], node_size=80)

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

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            for node in G.nodes:
                cont = G.nodes[node]['label']
                if cont and ax.contains_point((event.x, event.y)):
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
    start_time = time.time()
    json_directory = 'output/_五大类25小类json/_本义json'
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


    print("Loading vectors completed.")
    load_end = time.time()
    print(f"Loading vectors took {load_end - start_time} seconds.")

    print("Reducing dimensions...")
    reduction_start = time.time()
    vectors = np.concatenate(all_vectors, axis=0)
    reduced_vectors = reduce_dimensions(vectors)
    reduction_end = time.time()
    print(f"Dimensionality reduction took {reduction_end - reduction_start} seconds.")

    print("Plotting graph...")
    plot_start = time.time()
    plot_graph(reduced_vectors, all_labels, all_meanings)
    plot_end = time.time()
    print(f"Plotting took {plot_end - plot_start} seconds.")

    end_time = time.time()
    print(f"Total program runtime: {end_time - start_time} seconds.")

if __name__ == '__main__':
    main()
