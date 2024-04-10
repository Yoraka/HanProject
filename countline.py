# 统计文件夹下所有.py文件的代码行数
#
# 1. 递归遍历文件夹下所有文件
# 2. 读取文件内容，统计行数
# 3. 输出每个文件的代码行数
# 4. 输出所有文件的代码行数总和

import os

def count_line(file):
    with open(file, 'r', encoding='utf-8') as f:
        return len(f.readlines())
    
def count_line_in_dir(dir):
    total = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.py'):
                file = os.path.join(root, file)
                line = count_line(file)
                print(f'{file}: {line}')
                total += line
    print(f'Total: {total}')

count_line_in_dir('hpsrc')
