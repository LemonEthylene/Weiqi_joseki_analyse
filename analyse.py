import os
import re
import subprocess
import csv
import json
from pathlib import Path

# ===================== 配置区（按需修改）=====================
# 1. 棋谱根目录（批量扫描此目录下所有sgf，含子文件夹）
SGF_ROOT_DIR = r"C:\Users\13822\OneDrive\Desktop\WeiqiCode\gokifu_sgf\2006\test"
# 2. 你的python环境（和你运行命令的环境一致，直接用python即可）
PYTHON_EXE = "python"
# 3. 你的cli模块入口
CLI_MODULE = "src.cli.commands"
# 4. 输出结果文件
OUTPUT_CSV = "定式批量识别结果.csv"
OUTPUT_JSON = "定式全局统计.json"
# 5. 最小手数
MIN_STEP = 6
# ==========================================================

# 正则表达式：提取命令行输出的关键信息
pattern = re.compile(
r"来源角: (?P<corner>.+?)\s+"
r"定式ID: (?P<joseki_id>\w+)\s+"
r"匹配: (?P<match_step>\d+)\/(\d+)手\s+"
r"前缀: (?P<move_seq>.+?)\s+"
r"频率: (?P<freq>\d+)\s+概率: (?P<prob>[\d\.]+)%\s+",
    re.MULTILINE | re.DOTALL
)

def run_discover_command(sgf_path: str) -> str:
    """调用已有定式识别命令，返回原始输出"""
    cmd = [
        PYTHON_EXE,
        "-m", CLI_MODULE,
        "discover", sgf_path
    ]
    try:
        # 执行命令，捕获标准输出和错误
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="gbk",
            errors="replace",
            cwd=r"C:\Users\13822\OneDrive\Desktop\WeiqiCode\weiqi-joseki"  # 工作目录和你原命令一致
        )
        print("✅完成处理:")
        print(result.stdout)
        #print(result.stderr)
        return result.stdout
    except Exception as e:
        print(f"文件 {sgf_path} 调用失败: {str(e)}")
        return ""

def parse_joseki_output(sgf_file: str, raw_output: str) -> list[dict]:
    """解析单个文件的命令输出，提取结构化数据"""
    print("正则式提取中……")
    matches = pattern.findall(raw_output)
    if not matches: print("提取失败QAQ") 
    else: print("提取成功!")
    res_list = []
    for corner, jid, step, _, seq, freq, prob in matches:
        if(int(step) >= MIN_STEP):
            res_list.append({
                # "sgf文件": sgf_file,
                # "来源角": corner.strip(),
                "定式ID": jid.strip(),
                "匹配步数": step.strip(),
                "落子前缀": seq.strip(),
                # "单局频率": int(freq),
                # "概率%": float(prob)
            })
    return res_list

def batch_scan_sgf(root_dir: str):
    """批量遍历所有sgf文件，执行识别+解析"""
    all_results = []
    joseki_global_count = {}  # 全局统计：{定式ID: 出现次数}

    # 遍历所有sgf
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if fname.lower().endswith(".sgf"):
                sgf_full_path = str(Path(root) / fname)
                print(f"正在处理：{sgf_full_path}")
                # 调用命令+解析
                raw_out = run_discover_command(sgf_full_path)
                parsed = parse_joseki_output(sgf_full_path, raw_out)
                all_results.extend(parsed)
                # 全局计数
                for item in parsed:
                    jid = item["定式ID"]
                    joseki_global_count[jid] = joseki_global_count.get(jid, 0) + 1
    return all_results, joseki_global_count

def save_results(all_res: list[dict], global_stats: dict, output_csv, output_json):
    """保存csv明细 + json全局统计"""
    # 保存明细csv
    if all_res:
        headers = list(all_res[0].keys())
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_res)

     # 1. 构建 定式ID → 前缀 的映射（取第一次出现的前缀）
    joseki_prefix_map = {}
    for item in all_res:
        jid = item["定式ID"]
        prefix = item["落子前缀"]
        if jid not in joseki_prefix_map:
            joseki_prefix_map[jid] = prefix

    # 2. 按出现次数 **从高到低排序**
    sorted_joseki = sorted(
        global_stats.items(),
        key=lambda x: x[1],  # 按次数排序
        reverse=True         # 高 → 低
    )

    # 3. 构建最终JSON结构（带count + prefix）
    sorted_json_data = {}
    for jid, count in sorted_joseki:
        sorted_json_data[jid] = {
            "count": count,                # 出现次数
            "prefix": joseki_prefix_map.get(jid, "")  # 落子前缀
        }

    # 4. 写入JSON文件
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(sorted_json_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 批量处理完成！\n明细结果：{OUTPUT_CSV}\n✅ 已排序带前缀的JSON：{OUTPUT_JSON}")

if __name__ == "__main__":
    all_data, global_joseki = batch_scan_sgf(SGF_ROOT_DIR)
    save_results(all_data, global_joseki, OUTPUT_CSV, OUTPUT_JSON)