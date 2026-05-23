import os
import re
import subprocess
import csv
import json
from pathlib import Path
import analyse as ana

# 1. 棋谱根目录（批量扫描此目录下所有sgf，含子文件夹）
SGF_ROOT_DIR = r"C:\Users\13822\OneDrive\Desktop\WeiqiCode\gokifu_sgf"
RESULT_ROOT_DIR = r"C:\Users\13822\OneDrive\Desktop\WeiqiCode\results"
# 2. 最小手数
MIN_STEP = 6
# 3. 输出文件地址
OUTPUT_CSV = "定式批量识别结果.csv"
OUTPUT_JSON = "定式全局统计.json"
# 4. 遍历月份
START_MONTH = 1
END_MONTH = 1
# 5. 年份
START_YEAR = 2007
END_YEAR = 2007

if __name__ == "__main__":
    for year in range(START_YEAR, END_YEAR+1):
        dir = str(Path(SGF_ROOT_DIR) /str(year))

        all_data, global_joseki = ana.batch_scan_sgf(dir)

        csv_name, json_name = str(year)+".csv", str(year)+".json"
        csv_dir = str(Path(RESULT_ROOT_DIR) / csv_name)
        json_dir = str(Path(RESULT_ROOT_DIR) / json_name)

        ana.save_results(all_data, global_joseki, csv_dir, json_dir)
