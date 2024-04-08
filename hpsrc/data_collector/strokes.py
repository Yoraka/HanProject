import os
import json

class Strokes:
    def __init__(self, mode=0):
        self.data = {}
        self.strokes_character_counts = {}
        self.mode = mode
    
    def get_basic_data(self, unihan_irgs):
        root = os.getcwd()
        root = os.path.join(root, 'output/parsed_json')
        root = root.replace('\\', '/')
        # 遍历文件夹
        for file in os.listdir(root):
            if self.mode == 1:
                if not file.startswith('a'):
                    continue
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

                    if self.strokes_character_counts.get(stroke_count) is None:
                        self.strokes_character_counts[stroke_count] = 0
                    if total_meanings != 0:
                        self.strokes_character_counts[stroke_count] += 1

    def sort_by_strokes(self):
        # 对data进行排序, 根据stroke_count排序，而不是total_meanings
        sorted_data = {k: v for k, v in sorted(self.data.items(), key=lambda item: item[0])}
        self.data = sorted_data

        sorted_strokes_character_counts = {k: v for k, v in sorted(self.strokes_character_counts.items(), key=lambda item: item[0])}
        self.strokes_character_counts = sorted_strokes_character_counts

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

        #print(x, y)

        data_ratio = {k: results_dict[k] / self.strokes_character_counts[k] if self.strokes_character_counts[k] else 0 for k in results_dict.keys()}
        x_data_ratio = np.array(list(map(int, data_ratio.keys())))
        y_data_ratio = np.array(list(data_ratio.values()))

        # 把y为0的数据去掉
        x_data_ratio = x_data_ratio[y_data_ratio > 0]
        y_data_ratio = y_data_ratio[y_data_ratio > 0]

        # 打印升序sort后的数据，以x:y的形式
        data1 = dict(results_dict)
        data1 = {int(k): v for k, v in data1.items()}
        data1 = sorted(data1.items())
        print('Data1:', data1)
        data2 = dict(self.strokes_character_counts)
        # 将key转为int
        data2 = {int(k): v for k, v in data2.items()}
        data2 = sorted(data2.items())
        print('Data2:', data2)
        print('Data ratio:', dict(zip(x_data_ratio, y_data_ratio)))

        print(x_data_ratio, y_data_ratio)

        # Plotting the scatter plot
        # 分别为左右轴
        # Plotting the scatter plot
        # Set up the figure and the left axis
        fig, ax1 = plt.subplots()

        # Plot the total meanings on the left axis
        ax1.scatter(x, y, marker='x', color='blue', label='总释义数 数据点')
        ax1.set_xlabel('笔画数')
        # Set the label for the left y-axis
        ax1.set_ylabel('总释义数', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        #plt.scatter(x, y, marker='x', color='blue', label='Data points')
        #plt.scatter(x_data_ratio, y_data_ratio, marker='o', color='green', label='Meaning points')
        ax2 = ax1.twinx()
        ax2.scatter(x_data_ratio, y_data_ratio, marker='o', color='green', label='平均每字释义数 数据点')
        ax2.set_ylabel('平均每字释义数', color='green')
        ax2.tick_params(axis='y', labelcolor='green')

        # 使用幂律分布绘制笔画-释义关系图，要有最佳拟合函数与相关系数
        # 注意！要求拟合达到的相关系数为0.9以上
        def power_law_fit(x, y, threshold=0.8):
        # 注意！要求拟合达到的相关系数为0.9以上
            import numpy as np
            from scipy.optimize import curve_fit

            def power_law(x, a, b):
                return a * x ** b

            popt, _ = curve_fit(power_law, x, y)
            a, b = popt

            # 相关系数
            correlation_coef_power = np.corrcoef(y, power_law(x, *popt))[0, 1]

            if correlation_coef_power < threshold:
                a = b = 0

            return a, b, correlation_coef_power
        
        a, b, correlation_coef_power = power_law_fit(x_data_ratio, y_data_ratio)
        x_fit_power = np.linspace(min(x_data_ratio), max(x_data_ratio), 100)
        y_fit_power = a * x_fit_power ** b
        # 设置竖轴为右轴（分开显示）
        ax2.plot(x_fit_power, y_fit_power, 'g--', label='幂律拟合 (a={:.2f}, b={:.2f}, r^2={:.2f})'.format(a, b, correlation_coef_power))
        
        # Finding the best fit
        mu, sigma, a = self.find_best_fit_normal(x, y)
        #fit_distributions(x, y)
        #best_dist, best_popt, best_dist_func = self.fit_distributions(x, y)
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = a * np.exp(-0.5 * ((x_fit - mu) / sigma) ** 2)
        ax1.plot(x_fit, y_fit, 'b--', label='正态分布拟合 (mu={:.2f}, sigma={:.2f})'.format(mu, sigma))

        # Setting the font
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        if self.mode == 0:
            # Set the left y-axis limit
            ax1.set_ylim(0, 7500)

            # Set the right y-axis limit based on its own data range
            ax2.set_ylim(0, 5)

            ax1.set_xlim(0, 65)
            ax2.set_xlim(0, 65)
        else:
            # Set the left y-axis limit
            ax1.set_ylim(0, 1000)

            # Set the right y-axis limit based on its own data range
            ax2.set_ylim(0, 16)

            ax1.set_xlim(0, 32)
            ax2.set_xlim(0, 32)

        # Adding labels, title, and legend
        if self.mode == 0:
            fig.suptitle('全部部首笔画-释义关系图')
        else:
            fig.suptitle('五部首笔画-释义关系图')
        # 在ax1上添加图例
        ax1.legend(loc='upper left', bbox_to_anchor=(0.75, 0.95), borderaxespad=0.)

        # 在ax2上添加图例
        ax2.legend(loc='upper left', bbox_to_anchor=(0.75, 0.85), borderaxespad=0.)

        # Adding dashed grid lines
        ax1.grid(True, linestyle='--', alpha=0.6)

        # Removing the plot frame while keeping the axes
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)

        # Display the axes
        ax1.axhline(0, color='black', linewidth=0.5)
        ax1.axvline(0, color='black', linewidth=0.5)

        # Displaying the plot
        plt.show()

    def save_data(self):
        if self.mode == 1:
            return
        # 将笔画-释义数据保存到json文件
        root = os.getcwd()
        root = os.path.join(root, 'output')
        root = root.replace('\\', '/')
        if not os.path.exists(f'{root}/data_json'):
            os.makedirs(f'{root}/data_json')
        with open(f'{root}/data_json/strokes_meanings_data.json', 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)