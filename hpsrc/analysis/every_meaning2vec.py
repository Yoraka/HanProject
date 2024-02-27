import os
import json
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def load_data(file_paths):
    data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            for entry in json_data:
                for definition in entry['definitions']:
                    for meaning in definition['meanings']:
                        data.append(meaning)
    return data

def vectorize_data(data):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(data)
    return vectors.toarray(), vectorizer.get_feature_names_out()

def reduce_dimensions(vectors, method='pca', n_components=2):
    if method == 'pca':
        reducer = PCA(n_components=n_components)
    elif method == 'tsne':
        reducer = TSNE(n_components=n_components, perplexity=30)
    reduced_vectors = reducer.fit_transform(vectors)
    return reduced_vectors


def plot_graph(reduced_vectors, labels, file_paths):
    # Create a color map for each file
    colors = ['red', 'green', 'blue', 'orange', 'purple']
    color_map = {file_path: color for file_path, color in zip(file_paths, colors)}

    # Create a list of colors for each vector based on its label
    vector_colors = [color_map[label] for label in labels]

    # Adjust the transparency of the colors
    vector_colors = [(mcolors.to_rgba(color)[:3] + (0.5,)) for color in vector_colors]

    # Create a network graph
    G = nx.Graph()

    # Add nodes with attributes
    for i, vector in enumerate(reduced_vectors):
        G.add_node(i, vector=vector, label=labels[i], color=vector_colors[i])

    # Draw the graph without edges
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=False, node_color=[data['color'] for _, data in G.nodes(data=True)], node_size=50)
    plt.show()



def main():
    file_paths = [
        'output/parsed_json/a9_⼈部.json',
        'output/parsed_json/a30_⼝部.json',
        'output/parsed_json/a61_⼼部.json',
        'output/parsed_json/a76_⽋部.json',
        'output/parsed_json/a149_⾔部.json'
    ]

    data = load_data(file_paths)
    vectors, feature_names = vectorize_data(data)
    reduced_vectors = reduce_dimensions(vectors, method='tsne')

    # Create labels for each vector based on the file it came from
    labels = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            for entry in json_data:
                for definition in entry['definitions']:
                    count = len(definition['meanings'])
                    labels.extend([file_path] * count)

    plot_graph(reduced_vectors, labels, file_paths)

if __name__ == '__main__':
    main()

