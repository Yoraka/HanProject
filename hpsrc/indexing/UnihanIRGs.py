# 通过类似查询语句查询UnihanIRGSources.txt文件中的数据并返回
# Path: index/UnihanIRGs.py
# U+2A23A	kIRG_GSource	GHZ-74673.07
# U+2A23A	kIRG_TSource	T5-7C39
# U+2A23A	kRSUnicode	196.21
# U+2A23A	kTotalStrokes	32
# 输入Unicode编码. 输入的编码必须是16进制的, 例如: 4E00，再输入要查询的字段, 例如: kIRG_GSource，返回查询结果
import re
class UnihanIRGs:
    def __init__(self):
        self.data = {}
        with open('./data/Unihan/Unihan_IRGSources.txt', 'r', encoding='utf-8') as file:
            for line in file:
                # 如果遇到以#开头的行就跳过
                if line.startswith('#'):
                    continue
                # 尝试切割line为三部分，如果切割失败就打印切割失败的行
                try:
                    group = re.split(r'\s+', line)
                    unicode = group[0]
                    field = group[1]
                    value = group[2]
                except:
                    print(line)

                if unicode not in self.data:
                    self.data[unicode] = {}
                self.data[unicode][field] = value
    def query_unihan_irg_sources(self, unicode, field):
        if unicode in self.data and field in self.data[unicode]:
            return self.data[unicode][field]
        return None