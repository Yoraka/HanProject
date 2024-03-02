import json
import os
from gensim.models import keyedvectors
import hanlp
import numpy as np

def load_models_and_data():
    tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    ft_model = keyedvectors.KeyedVectors.load_word2vec_format('M:\XZS\cc.zh.300.vec.gz')
    with open('./data/stopwords.txt', 'r', encoding='utf-8') as file:
        stopwords = file.read().splitlines()
    return tok, ft_model, stopwords

def get_sentence_vector(words, model):
    vecs = [model[word] for word in words if word in model]
    if vecs:
        vecs = np.array(vecs)
        return np.mean(vecs, axis=0)
    else:
        return np.zeros(model.vector_size)

def process_meanings(meanings, tok, model, stopwords):
    cleaned_meanings = []
    meaning = ' '.join(meanings)
    words = tok(meaning)
    cleaned_words = [word for word in words if word not in stopwords]
    cleaned_meanings.append(get_sentence_vector(cleaned_words, model))
    return cleaned_meanings

def process_json_file(json_file, tok, ft_model, stopwords, output_dir):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        character = entry['character']
        definitions = entry.get('definitions', [])
        for definition in definitions:
            meanings = definition.get('meanings', [])
            if meanings:
                vectors = [process_meanings([meaning], tok, ft_model, stopwords)[0] for meaning in meanings]
                definition['vec'] = [','.join(map(str, vec)) for vec in vectors]
            else:
                definition['vec'] = []

    output_file = os.path.join(output_dir, os.path.basename(json_file))
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"完成处理文件: {json_file}，结果保存在: {output_file}")

def process_directory(subdir_path, tok, ft_model, stopwords, base_output_dir):
    subdir_name = os.path.basename(subdir_path)
    output_dir = os.path.join(base_output_dir, f"{subdir_name}_with_vec")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith(".json")]
    for json_file in json_files:
        process_json_file(json_file, tok, ft_model, stopwords, output_dir)

def run():
    print("运行程序...")
    base_directory = "output\_五大类25小类json"
    base_output_dir = "output\_五大类25小类json_with_vec"
    if not os.path.exists(base_output_dir):
        os.makedirs(base_output_dir)

    tok, ft_model, stopwords = load_models_and_data()

    for subdir in os.listdir(base_directory):
        subdir_path = os.path.join(base_directory, subdir)
        if os.path.isdir(subdir_path):
            print(f"正在处理目录: {subdir_path}")
            process_directory(subdir_path, tok, ft_model, stopwords, base_output_dir)



if __name__ == "__main__":
    run()
