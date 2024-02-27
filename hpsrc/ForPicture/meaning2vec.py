import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import os



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

def save_vectors(vectors, feature_names, file_path):
    # 确保文件所在的目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # 保存向量和特征名称到文件
    np.savez_compressed(file_path, vectors=vectors, feature_names=feature_names)

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
    save_vectors(vectors, feature_names, 'output/vectors/vector_data.npz')

if __name__ == '__main__':
    main()
