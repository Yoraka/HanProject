import jieba
import collections
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
import os
import json

radicals = ['a9_⼈', 'a30_⼝', 'a61_⼼', 'a76_⽋', 'a149_⾔']

def run(input_text, radical):
    #获取根目录
    root = os.getcwd()
    #拼接parsed_json文件夹路径
    root = os.path.join(root, 'output/词频')
    #转路径\\为/
    root = root.replace('\\', '/')
    # 获取当前路径
    now = os.path.dirname(__file__)
    # 素材路径
    test_text = input_text
    test_stop = f'{now}/stopwords.txt'  # 停用词
    test_mask = f'{now}/blue_circle.png'      # 底板图片素材
    test_font = f'{now}/SourceHanSansSC-Normal.otf'    # 字体

    # 读取处理文本和停用词

    text = test_text

    STOPWORDS = open(test_stop, encoding='utf8').read().split()

    # 分词和过滤
    # 筛选结果为不在停用词范围内且长度大于0
    # 筛去结果里含有"切"的
    word_list = []
    for word in jieba.cut(text):
        if word not in set(STOPWORDS) and len(word) > 0 and word != ' ' and ('切' not in word):
            word_list.append(word)

    # 统计词频
    word_counts = collections.Counter(word_list)
    # 将词频排序并输出到txt文件
    # 检查是否存在词频统计文件夹，不存在则创建
    if not os.path.exists(root):
        os.makedirs(root)
    with open(f'{root}/{radical}部词频统计.txt', 'w', encoding='utf8') as f:
        for k, v in word_counts.items():
            f.write(f'{k} {v}\n')

    # 选出频率前10的词
    word_counts_top100 = word_counts.most_common(10)


    # 读取图片并提取图片颜色
    im_mask = np.array(Image.open(test_mask))
    im_colors = ImageColorGenerator(im_mask)

    # 制作词云

    my_cloud = WordCloud(
        background_color='white',  # 设置背景颜色  默认是black
        mask=im_mask,              # 设置图片底板
        width=300, height=300,     #
        max_words=20,              # 词云显示的最大词语数量
        font_path=test_font,      # 设置字体  显示中文
        max_font_size=50,          # 设置字体最大值
        min_font_size=10,          # 设置字体最小值
        random_state=20            # 设置随机生成状态，即多少种配色方案
    ).generate_from_frequencies(word_counts)

    my_cloud.recolor(color_func=im_colors)  # 改变文字颜色

    # 显示生成的词云
    ax = plt.imshow(my_cloud)

    # 显示设置词云图中无坐标轴
    plt.axis('off')
    # 保存图片
    ax.figure.savefig(f'{root}/{radical}部词云.png', bbox_inches='tight', dpi=150)

# 从output的parsed_json中获取五个部首（函数每次处理一个部首）所有的meanings并拼接起来(用一个空格拼接)传入run函数
def get_all_meanings(radical):
    #获取根目录
    root = os.getcwd()
    #拼接parsed_json文件夹路径
    root = os.path.join(root, 'output')
    #转路径\\为/
    root = root.replace('\\', '/')
    meanings = []
    with open(f'{root}/parsed_json/{radical}部.json', 'r', encoding='utf8') as f:
        data = json.load(f)
    for key in data:
        if 'definitions' in key:
            for definition in key['definitions']:
                meanings.append(definition['meanings'])

    # 使用列表推导式将每个子列表转换为字符串
    flattened_meanings = [' '.join(sublist) for sublist in meanings]
    ret_string = ' '.join(flattened_meanings)
    # 确保返回的字符串中没有[]''这样的字符
    return ret_string.replace('[', '').replace(']', '').replace('\'', '')

if __name__ == '__main__':
    for radical in radicals:
        run(get_all_meanings(radical), radical)