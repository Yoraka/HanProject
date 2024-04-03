import numpy as np
from gensim.models import keyedvectors
import json
import os

import numpy as np
from gensim.models import keyedvectors
import json
import os

# 创建输出目录如果它不存在
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# FastText模型路径
ft_model_path = 'M:\XZS\cc.zh.300.vec.gz'
# 加载FastText模型
ft_model = keyedvectors.KeyedVectors.load_word2vec_format(ft_model_path)

# 定义部首及其对应字的字典
radical_to_chars = {
    '口': ['口', '嘴'],  
    '欠': ['欠', '呵欠','哈欠','想念','缺少','亏欠'],  
    '人': ['人', '亻'],
    '心': ['心', '忄','内心','心中','心脏','心情','心绪','思虑','谋划'],
    '言': ['言', '讠','訁','说','讲']
}

# 准备一个空字典来保存所有的词向量
radical_vectors = {}

# 对于每个部首，计算其对应字的词向量的平均值
for radical, chars in radical_to_chars.items():
    vectors = []
    for char in chars:
        if char in ft_model:
            char_vector = ft_model[char]
            vectors.append(char_vector)
        else:
            vectors.append(np.zeros(ft_model.vector_size))
    
    # 计算平均向量
    if vectors:
        average_vector = np.mean(vectors, axis=0)
        radical_vectors[radical] = average_vector.tolist()
    else:
        radical_vectors[radical] = np.zeros(ft_model.vector_size).tolist()

# 将字典保存到JSON文件中
with open(os.path.join(output_dir, '5radicals.json'), 'w', encoding='utf-8') as file:
    json.dump(radical_vectors, file, ensure_ascii=False, indent=4)

print("词向量已成功写入到output\\5radicals.json")
