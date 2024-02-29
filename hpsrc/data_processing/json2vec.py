import json
import os
import pandas as pd
import numpy as np
from gensim.models import keyedvectors
import hanlp
import re

def remove_enclosed_text(sentence):
    # 使用正则表达式匹配并去除被《》或〔〕包围的内容
    cleaned_sentence = re.sub(r'《[^》]*》|〔[^〕]*〕', '', sentence)
    return cleaned_sentence

def load_models_and_data():
    tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    ft_model = keyedvectors.KeyedVectors.load_word2vec_format('E:/traditionalChineseDl/cc.zh.300.vec.gz')
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
    for meaning in meanings:
        meaning = remove_enclosed_text(meaning)
        words = tok(meaning)
        cleaned_words = [word for word in words if word not in stopwords]
        cleaned_meanings.append(get_sentence_vector(cleaned_words, model))
    return cleaned_meanings

def process_json_file(json_file, tok, ft_model, stopwords):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    all_meanings_vec = []
    all_characters = []
    empty_meanings = []
    
    for entry in data:
        character = entry['character']
        definitions = entry.get('definitions', [])
        if len(definitions) != 0:
            for definition in definitions:
                meanings = definition.get('meanings', [])
                meanings_vec_list = process_meanings(meanings, tok, ft_model, stopwords)
                all_meanings_vec.extend(meanings_vec_list)
                if meanings_vec_list:
                    character_vec = np.mean(np.array(meanings_vec_list), axis=0)
                else:
                    character_vec = np.zeros(ft_model.vector_size)
                all_characters.append({'character': character, 'meanings_vec_average': character_vec})
        else:
            empty_meanings.append(character)

    with open('./output/empty_meanings.txt', 'w', encoding='utf-8') as file:
        for character in empty_meanings:
            file.write(character + '\n')
        print(f'Empty meanings for {len(empty_meanings)} characters, output to ./output/empty_meanings.txt')

    return all_meanings_vec, all_characters

def process_file(json_file, tok, ft_model, stopwords):
    print('start processing')
    return process_json_file(json_file, tok, ft_model, stopwords)

def run():
    json_files = [os.path.join(root, file) for root, dirs, files in os.walk("./output/parsed_json") for file in files if file.endswith(".json")]
    tok, ft_model, stopwords = load_models_and_data()
    # 确保 vec 目录存在
    vec_directory = './output/vec'
    if not os.path.exists(vec_directory):
        os.makedirs(vec_directory)

    # 单进程处理文件
    for json_file in json_files:
        all_meanings_vec, all_characters = process_file(json_file, tok, ft_model, stopwords)
        filename = os.path.splitext(os.path.basename(json_file))[0]

        # 保存所有意义的向量到 CSV
        df_meanings = pd.DataFrame(all_meanings_vec)
        df_meanings.to_csv(os.path.join(vec_directory, f'{filename}_meanings_vec.csv'), index=False)

        # 保存所有字符的平均向量到 CSV
        df_characters = pd.DataFrame(all_characters)
        df_characters.to_csv(os.path.join(vec_directory, f'{filename}_characters_vec.csv'), index=False)

    return 1

    return 1