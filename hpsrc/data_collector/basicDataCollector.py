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

        rhyme_book_notNone = 0
        for key in self.data:
            with open(f'{root}/{key}_{self.data[key]["部首"]}.json', 'r') as f:
                json_data = json.load(f)
                self.data[key]['汉字个数'] = len(json_data)
                for word in json_data:
                    #先判断有无definitions字段
                    if 'definitions' not in word:
                        continue
                    #再判断variants和synonyms字段里是不是有内容
                    #比如        "synonyms": [
                    #                   "鬒"
                    #                   ],
                    #这样有内容的就要跳过
                    #比如        "synonyms": [],
                    #这样没有内容的就要继续处理
                    if word['variants'] or word['synonyms'] or word['special_entries']:
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
                        rhyme_book = concepts['rhyme_book']
                        if rhyme_book != None:
                            matches = self.match_special_patterns(rhyme_book)
                        else:
                            matches = None

                        if matches != None:
                            fanqies.append(matches)
                        else:
                            print('A:', concepts['rhyme_book'])
                            if concepts['rhyme_book'] != None:
                                rhyme_book_notNone += 1
                    character_utf8 = hex(ord(word['character']))
                    if total_meanings == 0:
                        continue
                    
                    self.data[key]['汉字'][word['character']] = {
                        '笔画': UnihanIRGs.query_unihan_irg_sources(f'U+{character_utf8[2:].upper()}', 'kTotalStrokes'),
                        '反切': fanqies,
                        '拼音': pinyins,
                        '释义总个数': total_meanings
                    }
        print('rhyme_book_notNone:', rhyme_book_notNone)
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

    def match_special_patterns(self, text):
        # 匹配“音”的后一个字（包括音字）
        index_yin = text.find('音')
        if index_yin != -1 and index_yin + 1 < len(text):
            return text[index_yin:index_yin+2]

        # 匹配“切”的前面三个字（包括切字）
        index_qie = text.find('切')
        if index_qie != -1 and index_qie - 2 >= 0:
            return text[index_qie-2:index_qie+1]

        # 匹配“反”的前面三个字（包括反字）
        index_fan = text.find('反')
        if index_fan != -1 and index_fan - 3 >= 0:
            return text[index_fan-2:index_fan+1]
        
        return None
    
    def data_to_csv(self):
        print('data_to_csv')
        #获取根目录
        root = os.getcwd()
        #拼接parsed_json文件夹路径
        root = os.path.join(root, 'output')
        #转路径\\为/
        root = root.replace('\\', '/')
        #检查是否有data_csv文件夹，没有则创建
        if not os.path.exists(f'{root}/data_csv'):
            os.makedirs(f'{root}/data_csv')
        #保存到output的data_csv文件夹中
        for key in self.data:
            with open(f'{root}/data_csv/{key}_{self.data[key]["部首"]}.csv', 'w') as f:
                f.write('汉字,笔画,反切,拼音,释义总个数\n')
                for word in self.data[key]['汉字']:
                    #反切和拼音可能有多个，所以要以数组形式存储，但是写入csv文件时数组元素之间只能用空格分隔
                    #不能直接{self.data[key]["汉字"][word]["反切"]},这样多个反切会以数组形式写入csv文件,会以逗号分隔,而不是空格,但也要注意反切和拼音为空的情况
                    f.write(f'{word},{self.data[key]["汉字"][word]["笔画"]},')
                    if self.data[key]["汉字"][word]["反切"] != None:
                        if len(self.data[key]["汉字"][word]["反切"]) == 1:
                            f.write(self.data[key]["汉字"][word]["反切"][0])
                        else:
                            f.write(' '.join(self.data[key]["汉字"][word]["反切"]))
                    else:
                        f.write(' ')
                    if self.data[key]["汉字"][word]["拼音"] != None:
                        if len(self.data[key]["汉字"][word]["拼音"]) == 1:
                            f.write(f',{self.data[key]["汉字"][word]["拼音"][0]}')
                        else:
                            filtered_pinyin_list = [item for item in self.data[key]["汉字"][word]["拼音"] if item is not None]
                            f.write(',')
                            f.write(' '.join(filtered_pinyin_list))
                    else:
                        f.write(' ')
                    f.write(f',{self.data[key]["汉字"][word]["释义总个数"]}\n')
        print('data_to_csv end')

#end

#start
if __name__ == '__main__':
    collector = BasicDataCollector()
    unihanIRGs = UnihanIRGs()
    data = collector.collect_data(unihanIRGs)
    collector.data_to_csv()
    collector.save_data()
    
#end