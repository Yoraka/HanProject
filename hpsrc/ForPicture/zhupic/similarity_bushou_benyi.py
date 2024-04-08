import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 设置中文显示字体
font_path = "C:/Windows/Fonts/MSYH.TTC"  # 确保这个路径在你的机器上是正确的
chinese_font = FontProperties(fname=font_path)

# 定义目录路径
output_dir = 'output/similarity'

# 存储部首和平均相似度的字典
radical_avg_similarity = {}

# 遍历输出目录中的所有CSV文件
for filename in os.listdir(output_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(output_dir, filename)
        # 读取CSV文件
        df = pd.read_csv(file_path)
        # 提取平均相似度（第二行的第三列）
        avg_similarity = float(df.iloc[0, 2])
        radical = filename.split('_')[0]  # 从文件名中提取部首名称
        radical_avg_similarity[radical] = avg_similarity

# 绘制柱状图
plt.figure(figsize=(10, 6))
bars = plt.bar(radical_avg_similarity.keys(), radical_avg_similarity.values(), color='skyblue')
# 在每个柱子上方显示具体数值
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 5), va='bottom')
plt.xlabel('部首', fontproperties=chinese_font)
plt.ylabel('平均相似度', fontproperties=chinese_font)
plt.title('不同部首的平均相似度', fontproperties=chinese_font)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

