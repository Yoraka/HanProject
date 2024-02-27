import hanlp
from gensim import models as keyedvectors
import numpy as np
# test data
text =  {
        "character": "主",
        "variants": [],
        "synonyms": [],
        "definitions": [
            {
                "type": "multi_sound_multi_meaning",
                "pinyin": "zhǔ",
                "rhyme_book": "《廣韻》之庾切，上麌章。侯部。",
                "meanings": [
                    "灯心",
                    "家长",
                    "主人",
                    "首领，为首的人",
                    "君主",
                    "公卿大夫及其正妻",
                    "物主",
                    "当事人",
                    "事物的根本",
                    "死人的牌位",
                    "公主的简称",
                    "掌管，主持",
                    "主张",
                    "守",
                    "主象，预示（吉凶祸福、自然变化等）",
                    "主婚",
                    "中医术语，主治",
                    "专一",
                    "从自身出发的",
                    "基督教徒对*耶稣*、伊斯兰教教徒对*真主*的称呼",
                    "姓"
                ]
            },
            {
                "type": "multi_sound_multi_meaning",
                "pinyin": "zhù",
                "rhyme_book": "《集韻》朱戍切，去遇章。侯部。",
                "meanings": [
                    "量词"
                ]
            }
        ],
        "special_entries": []
    }

def load_models_and_data():
    tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
    ft_model = keyedvectors.KeyedVectors.load_word2vec_format('E:/traditionalChineseDl/cc.zh.300.vec.gz')
    with open('data/stopwords.txt', 'r', encoding='utf-8') as file:
        stopwords = file.read().splitlines()
    return tok, ft_model, stopwords

def get_sentence_vector(words, model):
    vecs = [model[word] for word in words if word in model]
    if vecs:
        vecs = np.array(vecs)
        return np.mean(vecs, axis=0)
    else:
        return np.zeros(model.vector_size)
    
if __name__ == "__main__":
    tok, ft_model, _ = load_models_and_data()
    print('begin')
    #将text中的meanings元素合成为一个str
    meanings1 = text['definitions'][0]['meanings']
    meanings_str1 = ' '.join(meanings1)
    ret1 = get_sentence_vector(tok(meanings_str1), ft_model)
    meanings2 = text['definitions'][1]['meanings']
    meanings_str2 = ' '.join(meanings2)
    ret2 = get_sentence_vector(tok(meanings_str2), ft_model)
    # 打印结果
    print(ret1)
    print(ret2)
    # 计算余弦相似度
    sim = np.dot(ret1, ret2) / (np.linalg.norm(ret1) * np.linalg.norm(ret2))
    print(sim)
    print('end')