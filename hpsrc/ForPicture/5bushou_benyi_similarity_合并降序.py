import os
import pandas as pd

def process_csv_files(input_dir, output_file):
    # 初始化空的DataFrame用于合并所有数据
    all_data = pd.DataFrame()

    # 遍历目录下的所有CSV文件
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_dir, file_name)

            # 读取CSV文件，跳过第二行，但保留列标题
            data = pd.read_csv(file_path, skiprows=[1])

            # 将当前文件的数据添加到总的DataFrame中
            all_data = pd.concat([all_data, data], ignore_index=True)

    # 按照 'similarity' 列的值降序排列数据
    all_data_sorted = all_data.sort_values(by='similarity', ascending=False)

    # 将排序后的数据保存到新的CSV文件中，包括列标题
    all_data_sorted.to_csv(output_file, index=False)

    # 打印成功消息
    print(f'数据已保存进 {output_file}')

# 指定输入和输出的路径
input_directory = 'output/similarity'
output_csv_file = 'output/5radicals_benyi.csv'

# 调用函数处理文件
process_csv_files(input_directory, output_csv_file)
