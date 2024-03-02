'''
#用于benyi
import json
import os
import pandas as pd
import numpy as np
from gensim.models import keyedvectors
import hanlp

def load_models_and_data():
    tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    ft_model = keyedvectors.KeyedVectors.load_word2vec_format('cc.zh.300.vec.gz')
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


def process_json_file(json_file, tok, ft_model, stopwords):
    with open(json_file, 'r', encoding='utf-8') as file:  # 指定编码为 utf-8
        data = json.load(file)
    all_meanings_vec = []
    empty_meanings = []
    
    for entry in data:
        character = entry['character']
        definitions = entry.get('definitions', [])
        if len(definitions) != 0:
            for definition in definitions:
                meanings = definition.get('meanings', [])
                if meanings:
                    for meaning in meanings:  # 处理每个释义
                        meaning_vec = process_meanings([meaning], tok, ft_model, stopwords)  # 将单个释义转换为向量
                        all_meanings_vec.extend(meaning_vec)
                else:
                    empty_meanings.append(character)

    with open('./output/emptymeanings.txt', 'w', encoding='utf-8') as file:
        for character in empty_meanings:
            file.write(character + '\n')
        print(f'Empty meanings for {len(empty_meanings)} characters, output to ./output/emptymeanings.txt')

    # 将所有释义的向量表示保存到 CSV 文件中
    df_meanings_vec = pd.DataFrame(all_meanings_vec)
    output_file = os.path.splitext(json_file)[0] + '_meanings_vec.csv'
    df_meanings_vec.to_csv(output_file, index=False)
    print(f'All meanings vectors saved to {output_file}')
    print(f"Finished processing file: {json_file}")  # 打印完成处理的文件名
    return all_meanings_vec


def process_file(json_file, tok, ft_model, stopwords):
    print(f"Processing file: {json_file}")
    return process_json_file(json_file, tok, ft_model, stopwords)

def run():
    print("Running the program...")
    json_files = [os.path.join(root, file) for root, dirs, files in os.walk("output\_五大类25小类json\_本义json") for file in files if file.endswith(".json")]
    tok, ft_model, stopwords = load_models_and_data()
    # 确保 vec 目录存在
    vec_directory = './output/vec_for_pic'
    if not os.path.exists(vec_directory):
        os.makedirs(vec_directory)

    # 单进程处理文件
    print("JSON files to process:", json_files)
    for json_file in json_files:
        all_meanings_vec = process_file(json_file, tok, ft_model, stopwords)  # 只接收一个返回值
        filename = os.path.splitext(os.path.basename(json_file))[0]

        # 保存所有意义的向量到 CSV
        df_meanings = pd.DataFrame(all_meanings_vec)
        df_meanings.to_csv(os.path.join(vec_directory, f'{filename}vec_for_pic.csv'), index=False)

    return 1

if __name__ == "__main__":
    run()
'''


#用于everymeaning2vec
import json
import os
import pandas as pd
import numpy as np
from gensim.models import keyedvectors
import hanlp

def load_models_and_data():
    tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    ft_model = keyedvectors.KeyedVectors.load_word2vec_format('cc.zh.300.vec.gz')
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


def process_json_file(json_file, tok, ft_model, stopwords):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        character = entry['character']
        definitions = entry.get('definitions', [])
        for definition in definitions:
            meanings = definition.get('meanings', [])
            if meanings:
                vectors = [process_meanings([meaning], tok, ft_model, stopwords)[0] for meaning in meanings]
                # 将词向量转换为字符串，每个向量占一行
                definition['vec'] = [','.join(map(str, vec)) for vec in vectors]
            else:
                # 如果没有释义，添加一个空的词向量列表
                definition['vec'] = []

    # 将修改后的数据写回 JSON 文件
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Finished processing file: {json_file}")


def process_file(json_file, tok, ft_model, stopwords):
    print(f"Processing file: {json_file}")
    return process_json_file(json_file, tok, ft_model, stopwords)

def run():
    print("Running the program...")
    base_directory = "output\_五大类25小类json"
    json_files = [os.path.join(root, file)
                  for subdir in os.listdir(base_directory)
                  if os.path.isdir(os.path.join(base_directory, subdir))
                  for root, dirs, files in os.walk(os.path.join(base_directory, subdir))
                  for file in files if file.endswith(".json")]
    tok, ft_model, stopwords = load_models_and_data()
    # 确保 vec 目录存在
    vec_directory = './output/json_with_vec'
    if not os.path.exists(vec_directory):
        os.makedirs(vec_directory)

    # 单进程处理文件
    print("JSON files to process:", json_files)
    for json_file in json_files:
        all_meanings_vec = process_file(json_file, tok, ft_model, stopwords)  # 只接收一个返回值
        filename = os.path.splitext(os.path.basename(json_file))[0]

        # 保存所有意义的向量到 CSV
        df_meanings = pd.DataFrame(all_meanings_vec)
        df_meanings.to_csv(os.path.join(vec_directory, f'{filename}.csv'), index=False)

    return 1


if __name__ == "__main__":
    run()
