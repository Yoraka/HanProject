import os
import json

class Strokes:
    def __init__(self):
        self.data = {}
    
    def get_basic_data(self, unihan_irgs):
        root = os.getcwd()
        root = os.path.join(root, 'output/parsed_json')
        root = root.replace('\\', '/')
        # 遍历文件夹
        for file in os.listdir(root):
            # 获取文件路径
            file_path = os.path.join(root, file)
            # 打开文件
            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取文件
                data = json.load(f)
                for character_properties in data:
                    character = character_properties['character']
                    character_utf8 = hex(ord(character))
                    stroke_count = unihan_irgs.query_unihan_irg_sources(f'U+{character_utf8[2:].upper()}', 'kTotalStrokes')
                    total_meanings = 0
                    for concepts in character_properties['definitions']:
                        total_meanings += len(concepts['meanings'])
                    if stroke_count not in self.data:
                        self.data[stroke_count] = 0
                    # 在stroke_count的value中增加(直接加法)
                    self.data[stroke_count] += total_meanings

    def sort_by_strokes(self):
        # 对data进行排序, 根据stroke_count排序，而不是total_meanings
        sorted_data = {k: v for k, v in sorted(self.data.items(), key=lambda item: item[0])}
        self.data = sorted_data

        print(self.data)

    def fit_distributions(self, x, y):
        from scipy.stats import poisson, nbinom, lognorm
        from scipy.optimize import curve_fit
        import numpy as np
        x = np.array(x)
        y = np.array(y)
        if np.any(y <= 0):
            # 从y中删除非正值
            x = x[y > 0]
            y = y[y > 0]

        # 定义各种分布的拟合函数
        def poisson_f(x, mu):
            if mu < 0:
                return np.zeros_like(x)  # 保证mu为非负
            pmf = poisson.pmf(x, mu)
            pmf[np.isnan(pmf)] = 0  # 替换 NaN 值为0
            return pmf * len(y) * np.diff(poisson.ppf([0, 1], mu))

        def nbinom_f(x, n, p):
            if p <= 0 or p >= 1 or n < 0:
                return np.zeros_like(x)  # 保证p在(0,1)之间，n为非负
            pmf = nbinom.pmf(x, n, 1-p)
            pmf[np.isnan(pmf)] = 0  # 替换 NaN 值为0
            return pmf * len(y) * np.diff(nbinom.ppf([0, 1], n, 1-p))
            
        def lognorm_f(x, s, scale):
            return lognorm.pdf(x, s, scale=scale) * len(y) * np.diff(lognorm.ppf([0, 1], s, scale=scale))
        
        # 初始化最佳拟合参数和AIC值
        best_aic = np.inf
        best_fit = None
        
        # 泊松分布拟合
        popt_poisson, _ = curve_fit(poisson_f, x, y / y.sum(), p0=[np.mean(x)])
        
        # 负二项分布拟合
        popt_nbinom, _ = curve_fit(nbinom_f, x, y / y.sum(), p0=[1, np.mean(y / y.sum())])
        
        # 对数正态分布拟合，确保没有无效值
        s_est, loc_est, scale_est = lognorm.fit(y, floc=0)  # floc=0 固定位置参数为0
        popt_lognorm, _ = curve_fit(lognorm_f, x, y / y.sum(), p0=[s_est, scale_est])

        # 计算AIC值
        aic_poisson = -2 * np.sum(np.log(poisson_f(x, *popt_poisson))) + 2 * len(popt_poisson)
        aic_nbinom = -2 * np.sum(np.log(nbinom_f(x, *popt_nbinom))) + 2 * len(popt_nbinom)
        aic_lognorm = -2 * np.sum(np.log(lognorm_f(x, *popt_lognorm))) + 2 * len(popt_lognorm)
        
        # 找出最佳拟合
        for dist, aic in [('poisson', aic_poisson), ('nbinom', aic_nbinom), ('lognorm', aic_lognorm)]:
            if aic < best_aic:
                best_aic = aic
                best_fit = dist
        
        # 返回最佳拟合分布名称和参数
        if best_fit == 'poisson':
            return best_fit, popt_poisson, poisson_f
        elif best_fit == 'nbinom':
            return best_fit, popt_nbinom, nbinom_f
        elif best_fit == 'lognorm':
            return best_fit, popt_lognorm, lognorm_f

    # 用正态分布拟合
    def find_best_fit_normal(self, x, y):
        from scipy.optimize import curve_fit
        import numpy as np

        # Define the function to fit
        def normal(x, mu, sigma, a):
            return a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
        
        # Fit the data
        popt, _ = curve_fit(normal, x, y)
        mu, sigma, a = popt

        return mu, sigma, a

    def plot_strokes_and_meanings_dict_normal(self, results_dict):
        import matplotlib.pyplot as plt
        import numpy as np

        # Prepare data for plotting
        x = [int(k) for k in results_dict.keys()]
        y = list(results_dict.values())

        # 把y为0的数据去掉
        x = np.array(x)
        y = np.array(y)
        x = x[y > 0]
        y = y[y > 0]

        print(x, y)

        # Plotting the scatter plot
        plt.scatter(x, y, marker='x', color='blue', label='Data points')

        # Finding the best fit
        mu, sigma, a = self.find_best_fit_normal(x, y)
        #fit_distributions(x, y)
        #best_dist, best_popt, best_dist_func = self.fit_distributions(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = a * np.exp(-0.5 * ((x_fit - mu) / sigma) ** 2)
        plt.plot(x_fit, y_fit, 'r-', label=f'Best fit (mu={mu:.2f}, sigma={sigma:.2f})')

        # Setting the font
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        # Adding labels, title, and legend
        plt.xlabel('笔画数')
        plt.ylabel('释义数')
        plt.title('笔画-释义关系图')
        plt.legend()

        # Adding 虚线网格
        plt.grid(True, linestyle='--', alpha=0.6)

        # 取消掉图的框，只留数轴
        plt.box(False)
        # 要有数轴
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)

        # Displaying the plot
        plt.show()

    def save_data(self):
        # 将笔画-释义数据保存到json文件
        root = os.getcwd()
        root = os.path.join(root, 'output')
        root = root.replace('\\', '/')
        if not os.path.exists(f'{root}/data_json'):
            os.makedirs(f'{root}/data_json')
        with open(f'{root}/data_json/strokes_meanings_data.json', 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)