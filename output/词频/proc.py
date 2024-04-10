# 将每个词频csv前10行的数据保存到新的csv文件中
import os
import pandas as pd

def get_top_10_rows(file):
    df = pd.read_csv(file)
    if file.name.endswith('五部词频.csv'):
        return df.head(20)
    if len(df) < 10:
        return df.head(5)
    df = df.head(10)
    return df

def data_to_excel(data, file_path):# 保存为excel文件，不是csv
    file_name = file_path.split('.')[0] + '_top_10.xlsx'
    data.to_excel(file_name, index=False)

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    root = root.replace('\\', '/')
    # 打开词频文件夹
    dir = root
    files = os.listdir(dir)
    print(files)
    for file in files:
        if file.endswith('.csv'):
            file_path = f'{dir}/{file}'
            with open(f'{dir}/{file}', 'r') as f:
                print(file_path)
                data = get_top_10_rows(f)
                print(data)
                if not data.empty:
                    data_to_excel(data, file_path)
                    