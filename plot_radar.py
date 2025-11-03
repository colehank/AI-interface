# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === 1. 读取 Excel 文件 ===
file_path = "信效度结果.xlsx"  # 或完整路径
reliability_df = pd.read_excel(file_path, sheet_name="信度")
validity_df = pd.read_excel(file_path, sheet_name="效度")

# === 2. 替换模态名称为英文 ===
reliability_df['Unnamed: 0'] = reliability_df['Unnamed: 0'].replace({'文字': 'Text', '图片': 'Image', '视频': 'Video'})
validity_df['Unnamed: 0'] = validity_df['Unnamed: 0'].replace({'文字': 'Text', '图片': 'Image', '视频': 'Video'})

# === 3. 定义绘图函数 ===
def plot_radar(data, title):
    labels = ['O', 'C', 'E', 'A', 'N']
    num_vars = len(labels)

    # 计算每个维度的角度
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # 创建雷达图
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # 绘制不同模态的数据线
    for i, row in data.iterrows():
        values = row[labels].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=row['Unnamed: 0'])
        ax.fill(angles, values, alpha=0.1)

    # 设置图形样式
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0.5, 1)  # 设置显示范围为0.5-1
    ax.set_title(title, size=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1))
    plt.show()

# === 4. 绘制信度与效度雷达图 ===
plot_radar(reliability_df, "Reliability (OCEAN)")
plot_radar(validity_df, "Validity (OCEAN)")
#%%
