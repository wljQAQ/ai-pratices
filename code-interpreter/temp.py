import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

def analyze_and_visualize():
    # 识别运行平台和家目录
    home_dir = str(Path.home())
    data_path = './data.csv'
    
    # 读取数据
    df = pd.read_csv(data_path)
    
    # 生成描述性统计信息
    print("数据描述性统计信息：")
    print("=" * 50)
    print(df.describe())
    print("\n数据基本信息：")
    print("=" * 50)
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"数据类型:\n{df.dtypes}")
    print(f"缺失值统计:\n{df.isnull().sum()}")
    
    # 创建可视化图表
    plt.figure(figsize=(15, 10))
    
    # 数值列的分布图
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        # 直方图
        plt.subplot(2, 2, 1)
        for col in numeric_cols:
            plt.hist(df[col].dropna(), alpha=0.7, label=col)
        plt.title('数值变量分布')
        plt.legend()
        
        # 箱线图
        plt.subplot(2, 2, 2)
        df[numeric_cols].boxplot()
        plt.title('数值变量箱线图')
        plt.xticks(rotation=45)
    
    # 分类列的计数图（如果存在）
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        # 选择第一个分类列进行可视化
        cat_col = categorical_cols[0]
        plt.subplot(2, 2, 3)
        df[cat_col].value_counts().plot(kind='bar')
        plt.title(f'{cat_col} 分类分布')
        plt.xticks(rotation=45)
    
    # 相关性热力图（如果有多个数值列）
    if len(numeric_cols) > 1:
        plt.subplot(2, 2, 4)
        corr_matrix = df[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('变量相关性热力图')
    
    plt.tight_layout()
    
    # 保存图片
    output_dir = './'
    output_path = os.path.join(output_dir, 'data_analysis_plot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n可视化图表已保存至: {output_path}")
    return output_path

# 运行函数
result_path = analyze_and_visualize()
print(f"图片文件路径: {result_path}")