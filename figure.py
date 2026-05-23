import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from decimal import Decimal, getcontext
import matplotlib.cm as cm

# ====================== 【可修改配置】 ======================
JSON_DIR = "results"                 # JSON文件所在文件夹
START_YEAR = 2006              # 起始年份
END_YEAR = 2026                # 结束年份
FREQ_THRESHOLD = 0.0200          # 筛选阈值
MAX_LINES = 100                 # 最多画多少条折线（避免太乱）
# ===========================================================

# 解决中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取每年JSON，统计：每个定式每年次数 + 当年总次数
yearly_total = {
    2006: 2572,
    2007: 2709,
    2008: 2607,
    2009: 2007,
    2010: 2206,
    2011: 3078,
    2012: 4181,
    2013: 2791,
    2014: 1799,
    2015: 2232,
    2016: 2771,
    2017: 4127,
    2018: 5488,
    2019: 1969,
    2020: 2010,
    2021: 763,
    2022: 798,
    2023: 1454,
    2024: 1592,
    2025: 1443,
    2026: 272
}          #  key: 年份, value: 当年所有棋局总次数
opening_year_count = defaultdict(lambda: defaultdict(int))
threshold = Decimal(str(FREQ_THRESHOLD))

for year in range(START_YEAR, END_YEAR + 1):
    path = os.path.join(JSON_DIR, f"{year}.json")
    if not os.path.exists(path):
        print(f"跳过：{year}.json（不存在）")
        continue

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 计算当年总次数
    # total = sum(item["count"] for item in data.values())
    # yearly_total[year] = total

    # print(yearly_total)

    # 记录每个定式当年次数
    for opening_id, item in data.items():
        prefix = opening_id
        cnt = item["count"]
        opening_year_count[prefix][year] = cnt

# 2. 计算每个定式【每年的占比】，并筛选：至少一年 > 阈值
qualified_openings = []

for prefix in opening_year_count:
    # 计算该定式每年的占比
    year_freq = {}
    for year in yearly_total:
        cnt = opening_year_count[prefix][year]
        total = yearly_total[year]
        freq = Decimal(cnt) / Decimal(total) if total != 0 else 0
        year_freq[year] = float(freq)

    # 判断：是否至少有一年超过阈值
    if any(f > threshold for f in year_freq.values()):
        qualified_openings.append((prefix, year_freq))

# 3. 按“最高占比”排序，取前N个画图
qualified_openings.sort(key=lambda x: max(x[1].values()), reverse=True)
qualified_openings = qualified_openings[:MAX_LINES]

print(f"\n✅ 筛选完成：共 {len(qualified_openings)} 个定式满足 任意一年占比 > {FREQ_THRESHOLD:.1%}")

# 4. 构建绘图数据
years = sorted(yearly_total.keys())
df = pd.DataFrame(index=years)

for prefix, year_freq in qualified_openings:
    freq_list = [year_freq[y] for y in years]
    # 图例只显示前30个字符，避免太长
    label = prefix[:30] + "..." if len(prefix) > 30 else prefix
    df[label] = freq_list

# 5. 绘制折线图
plt.figure(figsize=(14, 8))

# soft_colors = ['#61d3e3', '#4192e3', '#71f341', '#49aa10', 
#                '#ebd320', '#8a8a00', '#ffa200', '#c37100',
#                '#ff7930', '#e35100', '#f361ff', '#db41c3',
#                '#a271ff', '#9241f3', '#cbcbcb', '#797979']

n_lines = len(qualified_openings)
cmap = cm.tab10
soft_colors = cmap(np.linspace(0, 1, n_lines))

for idx, col in enumerate(df.columns):
    c = soft_colors[idx % len(soft_colors)]
    plt.plot(
        df.index, df[col],
        marker='o', 
        markersize=3.5,
        linewidth=2.0,
        # color=c,
        label=col
    )

# 图表美化
# plt.title(f'围棋定式年度占比趋势图（至少一年频率 > {FREQ_THRESHOLD:.1%}）', fontsize=16)
plt.xlabel('年份', fontsize=14)
plt.ylabel('频率', fontsize=14)
plt.grid(True, alpha=0.3)
plt.xticks(years, rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=20)
# plt.text(0.02, 0.98, '定式ID', fontsize=16)
plt.tight_layout()

# 保存图片
plt.savefig('go_opening_freq_trend.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✅ 图表已保存：go_opening_freq_trend.png")