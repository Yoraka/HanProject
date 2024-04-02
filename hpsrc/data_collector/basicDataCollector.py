#收集5个部首的数据
#收集每个部首汉字个数，每个汉字有多少笔画，每个汉字的反切，每个汉字的拼音，每个汉字的释义个数，分本义，其他义项的个数
#数据从output里面的json文件中读取, 要求处理parsed_json文件夹中a9_人部, a30_口部, a61_心部, a76_手部, a149_木部的json文件
#json格式
#{
#    "部首": {
#        "部首": "部首",
#        "汉字个数": "汉字个数",
#        "汉字": {
#            "笔画": "笔画",
#            "反切": "反切",
#            "拼音": "拼音",
#            "释义总个数": "释义总个数",
#        }
#    }
#}
#start
import json
import os
import re
from hpsrc.indexing.UnihanIRGs import UnihanIRGs

class BasicDataCollector:
    def __init__(self):
        self.data = {
            'a9': {
                '部首': '⼈部',
                '汉字个数': 0,
                '汉字': {}
            },
            'a30': {
                '部首': '⼝部',
                '汉字个数': 0,
                '汉字': {}
            },
            'a61': {
                '部首': '⼼部',
                '汉字个数': 0,
                '汉字': {}
            },
            'a76': {
                '部首': '⽋部',
                '汉字个数': 0,
                '汉字': {}
            },
            'a149': {
                '部首': '⾔部',
                '汉字个数': 0,
                '汉字': {}
            }
        }
    
    def collect_data(self, UnihanIRGs):
        #获取根目录
        root = os.getcwd()
        #拼接parsed_json文件夹路径
        root = os.path.join(root, 'output/parsed_json')
        #转路径\\为/
        root = root.replace('\\', '/')
        for key in self.data:
            with open(f'{root}/{key}_{self.data[key]["部首"]}.json', 'r') as f:
                json_data = json.load(f)
                self.data[key]['汉字个数'] = len(json_data)
                for word in json_data:
                    #先判断有无definitions字段
                    if 'definitions' not in word:
                        continue
                    #word的笔画通过indexing文件夹中的UnihanIRGs类的query_unihan_irg_sources方法获取, 获取方法如下
                    # 通过类似查询语句查询UnihanIRGSources.txt文件中的数据并返回
                    # Path: indexing/UnihanIRGs.py
                    # U+2A23A	kIRG_GSource	GHZ-74673.07
                    # U+2A23A	kIRG_TSource	T5-7C39
                    # U+2A23A	kRSUnicode	196.21
                    # U+2A23A	kTotalStrokes	32
                    # 输入Unicode编码. 输入的编码必须是16进制的, 例如: 4E00，再输入要查询的字段, 例如: kTotalStrokes，返回查询结果

                    #word的示例如下：
                    '''
                    {
                        "character": "了",
                        "variants": [],
                        "synonyms": [],
                        "definitions": [
                            {
                                "type": "multi_sound_multi_meaning",
                                "pinyin": "liǎo",
                                "rhyme_book": "《廣韻》盧鳥切，上篠來。宵部。",
                                "meanings": [
                                    "走路时足胫相交",
                                    "结束；了结",
                                    "决定；决断",
                                    "聪明",
                                    "明白，懂得",
                                    "清楚，明晰",
                                    "快",
                                    "悬挂",
                                    "副词",
                                    "“瞭”的简化字"
                                ]
                            },
                            {
                                "type": "multi_sound_multi_meaning",
                                "pinyin": "le",
                                "rhyme_book": null,
                                "meanings": [
                                    "助词",
                                    "语气词"
                                ]
                            }
                        ],
                        "special_entries": []
                    },
                    '''
                    #word的反切通过获取word中的"rhyme_book": "《集韻》時忍切（",用re匹配》到切之间(包含切字)的内容，例如这里应该匹配到"時忍切"
                    #word的拼音通过获取word中的"pinyin",直接获取即可，有时有多个，可以以数组形式存储
                    #word的释义个数通过统计word中的"meanings"个数
                    total_meanings = 0
                    for concepts in word['definitions']:
                        total_meanings += len(concepts['meanings'])
                    pinyins = []
                    for concepts in word['definitions']:
                        pinyins.append(concepts['pinyin'])
                    fanqies = []
                    for concepts in word['definitions']:
                        try:
                            matches = re.search(r'》(.*?)切', concepts['rhyme_book']).group(1)
                            fanqies.append(matches)
                        except:
                            print(concepts['rhyme_book'])
                    character_utf8 = hex(ord(word['character']))
                    self.data[key]['汉字'][word['character']] = {
                        '笔画': UnihanIRGs.query_unihan_irg_sources(f'U+{character_utf8[2:].upper()}', 'kTotalStrokes'),
                        '反切': fanqies,
                        '拼音': pinyins,
                        '释义总个数': total_meanings
                    }
        return self.data
    
    def save_data(self):
        #获取根目录
        root = os.getcwd()
        #拼接parsed_json文件夹路径
        root = os.path.join(root, 'output')
        #转路径\\为/
        root = root.replace('\\', '/')
        #检查是否有data_json文件夹，没有则创建
        if not os.path.exists(f'{root}/data_json'):
            os.makedirs(f'{root}/data_json')
        #保存到output的data_json文件夹中
        with open(f'{root}/data_json/basic_data.json', 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
#end

#start
if __name__ == '__main__':
    collector = BasicDataCollector()
    UnihanIRGs = UnihanIRGs()
    data = collector.collect_data(UnihanIRGs)
    collector.save_data()
#end