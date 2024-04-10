# 获取basic_data.json里面的数据
import json
import os

keys = ['a9', 'a30', 'a61', 'a76', 'a149']
#获取basic_data.json数据
def get_basic_data():
    #获取根目录
    root = os.getcwd()
    #拼接basic_data.json文件路径
    root = os.path.join(root, 'output/data_json/basic_data.json')
    #转路径\\为/
    root = root.replace('\\', '/')
    #打开文件
    with open(root, 'r', encoding='utf-8') as f:
        #读取文件
        data = json.load(f)
    return data

#从basic_data里获得每个汉字的笔画，释义总个数，存入data数组
def get_basic_data_by_key(data, key):
    result = []
    strokes_character_count = {}
    #遍历data数组
    for character, properties in data[key]['汉字'].items():
        temp = []
        stroke_count = properties['笔画']
        meaning_count = properties['释义总个数']
        temp.append(stroke_count)
        temp.append(meaning_count)
        result.append(temp)

        if stroke_count not in strokes_character_count:
            strokes_character_count[stroke_count] = 0
        #在strokes_character_count的value中增加(直接加法)
        strokes_character_count[stroke_count] += 1

    return result, strokes_character_count

#按照笔画升序排序result数组
def sort_by_strokes(result):
    result.sort(key=lambda x: x[0])
    return result

def plot_strokes_and_meanings(result):
    import matplotlib.pyplot as plt
    
    # Convert stroke counts to integers and count occurrences
    counts = {}
    for strokes, meanings in result:
        strokes = int(strokes)
        key = (strokes, meanings)
        if key not in counts:
            counts[key] = 0
        counts[key] += 1
    
    # Prepare data for plotting
    x = []
    y = []
    sizes = []
    for (strokes, meanings), count in counts.items():
        x.append(strokes)
        y.append(meanings)
        sizes.append(count * 20)  # Adjust the size multiplier as needed
    
    # Plotting the scatter plot
    plt.scatter(x, y, s=sizes)
    # 设置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    
    # Adding labels and title
    plt.xlabel('笔画数')
    plt.ylabel('释义数')
    plt.title('笔画-释义关系图(点大小表示重叠于此的汉字个数)')
    
    # Adding grid lines for better readability
    plt.grid(False)
    
    # Displaying the plot
    plt.show()

# 用字典绘制笔画-释义关系图
def find_best_fit(x, y, max_degree=10, threshold=0.9):
    import numpy as np
    from sklearn.metrics import r2_score

    best_degree = 0
    best_r2 = 0
    best_poly = None

    for degree in range(1, max_degree + 1):
        coefficients = np.polyfit(x, y, degree)
        polynomial = np.poly1d(coefficients)
        y_pred = polynomial(x)
        r2 = r2_score(y, y_pred)

        if r2 > best_r2:
            best_degree = degree
            best_r2 = r2
            best_poly = polynomial

        if r2 > threshold:
            break

    return best_degree, best_poly, best_r2

# 用正态分布拟合
def find_best_fit_normal(x, y):
    from scipy.optimize import curve_fit
    import numpy as np

    def normal_distribution(x, mu, sigma, a):
        return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

    popt, _ = curve_fit(normal_distribution, x, y, p0=[np.mean(x), np.std(x), max(y)])
    mu, sigma, a = popt

    return mu, sigma, a

def plot_strokes_and_meanings_dict(results_dict, max_degree=10, threshold=0.98):
    import matplotlib.pyplot as plt
    import numpy as np

    # Convert stroke counts to integers and count occurrences
    counts = {}
    for strokes, meanings in results_dict.items():
        strokes = int(strokes)
        key = (strokes, meanings)
        if key not in counts:
            counts[key] = 0
        counts[key] += 1

    # Prepare data for plotting
    x = []
    y = []
    sizes = []
    for (strokes, meanings), count in counts.items():
        x.append(strokes)
        y.append(meanings)
        sizes.append(count * 20)  # Adjust the size multiplier as needed

    # Plotting the scatter plot
    plt.scatter(x, y, s=sizes, label='Data points')

    # Finding the best fit
    best_degree, best_poly, best_r2 = find_best_fit(x, y, max_degree, threshold)
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = best_poly(x_fit)
    plt.plot(x_fit, y_fit, 'r-', label=f'Best fit (degree {best_degree}, R²={best_r2:.2f})')

    # Setting the font
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # Adding labels, title, and legend
    plt.xlabel('笔画数')
    plt.ylabel('释义数')
    plt.title('笔画-释义关系图')
    # 副标题将函数的公式显示
    # 将best_poly转为字符串
    best_poly = str(best_poly)
    # 将第一个换行符前的字符全部删掉
    best_poly = best_poly[best_poly.find('\n') + 1:]
    def add_exponents(poly_str):
        # 使用正则表达式匹配所有的x并添加指数
        degree = poly_str.count('x')  # 计算x的个数，即最高次数
        def replace_x(match):
            nonlocal degree
            if degree > 1:
                result = f"x^{degree}"
            elif degree == 1:
                result = "x"
            degree -= 1
            return result

        import re
        formatted_poly_str = re.sub(r"x", replace_x, poly_str)
        return formatted_poly_str
    
    best_poly = add_exponents(best_poly)

    plt.suptitle(f'最佳拟合函数: {best_poly}', fontsize=10)
    plt.legend()

    # Adding grid lines
    plt.grid(False)

    # Displaying the plot
    plt.show()

# 使用幂律分布绘制笔画-释义关系图，要有最佳拟合函数与相关系数
def power_law_fit(x, y):
    import numpy as np
    from scipy.optimize import curve_fit

    def power_law(x, a, b):
        return a * x ** b

    popt, _ = curve_fit(power_law, x, y)
    a, b = popt

    # 相关系数
    correlation_coef_power = np.corrcoef(y, power_law(x, *popt))[0, 1]

    return a, b, correlation_coef_power

# 使用正态分布绘制笔画-释义关系图

def plot_strokes_and_meanings_dict_normal(results_dict, strokes_character_counts):
    import matplotlib.pyplot as plt
    import numpy as np

    # Convert stroke counts to integers and count occurrences
    counts = {}
    for strokes, meanings in results_dict.items():
        strokes = int(strokes)
        key = strokes
        value = meanings
        if key not in counts:
            counts[key] = 0
        counts[key] += value

    # 将strokes_character_counts转为字典，笔画数作为key唯一，字数合并作为value，key为int类型
    strokes_character_counts = {int(k): v for k, v in strokes_character_counts.items()}

    # 升序sort
    counts = dict(sorted(counts.items()))
    strokes_character_counts = dict(sorted(strokes_character_counts.items()))

    print(strokes_character_counts)
    print(counts)

    # 将y替换为与character_counts相除的值（每个笔画数的释义总数/字数总数）
    for strokes in counts.keys():
        counts[strokes] /= strokes_character_counts[strokes]

    print(counts)

    # Prepare data for plotting
    x = []
    y = []
    sizes = []
    for strokes in counts.keys():
        x.append(strokes)
        y.append(counts[strokes])
        #sizes.append(strokes_character_counts[strokes] * 20)  # Adjust the size multiplier as needed

    # Plotting the scatter plot
    plt.scatter(x, y, label='Data points')

    # Finding the best fit
    if 0 == 1:
        mu, sigma, a = find_best_fit_normal(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = a * np.exp(-0.5 * ((x_fit - mu) / sigma) ** 2)
        plt.plot(x_fit, y_fit, 'r-', label=f'Best fit (mu={mu:.2f}, sigma={sigma:.2f})')
    else:
        a, b, r2 = power_law_fit(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = a * x_fit ** b
        plt.plot(x_fit, y_fit, 'r-', label=f'Best fit (a={a:.2f}, b={b:.2f}, R²={r2:.2f})')

    # Setting the font
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # Adding labels, title, and legend
    plt.xlabel('笔画数')
    plt.ylabel('平均妹子释义数')
    plt.title('笔画-释义关系图')
    plt.legend()

    # Adding grid lines
    plt.grid(False)

    # Displaying the plot
    plt.show()

if __name__ == '__main__':
    data = get_basic_data()
    results = []
    strokes_character_counts = {}
    for key in keys:
        result, strokes_character_count = get_basic_data_by_key(data, key)
        results.extend(result)
        for strokes, count in strokes_character_count.items():
            if strokes not in strokes_character_counts:
                strokes_character_counts[strokes] = 0
            strokes_character_counts[strokes] += count
    results = sort_by_strokes(results)
    plot_strokes_and_meanings(results)
    # 直接将results转为字典，笔画数作为key唯一，释义数合并作为value
    results_dict = {}
    for strokes, meanings in results:
        if strokes not in results_dict:
            results_dict[strokes] = 0
        results_dict[strokes] += meanings
    plot_strokes_and_meanings_dict(results_dict)
    plot_strokes_and_meanings_dict_normal(results_dict, strokes_character_counts=strokes_character_counts)
