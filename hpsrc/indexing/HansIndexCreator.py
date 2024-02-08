import pickle
import docx2txt

def create_index(doc_path):
    text = docx2txt.process(doc_path)
    index = {}
    current_key = None
    current_value = ""

    for line in text.split('\n'):
        if '##' in line:
            if current_key is not None:
                index[current_key] = current_value.strip()
            current_key, current_value = line.split('##', 1)
        else:
            current_value += '\n' + line

    # 添加最后一个条目
    if current_key is not None:
        index[current_key] = current_value.strip()

    return index

def save_index_to_file(index, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(index, file)

def run():
    # 构建并保存索引
    doc_path = '.\data\漢語大字典文字版.docx'
    index_file_path = '.\output\index_file.pkl'
    index = create_index(doc_path)
    save_index_to_file(index, index_file_path)
    return 1