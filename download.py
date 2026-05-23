import os
import sys
import random
import time
import requests
from bs4 import BeautifulSoup

# ====================== 配置项 ======================
START_YEAR = 2018
END_YEAR = 2018
START_MONTH = 9
END_MONTH = 9
START_PAGE = 31       # 开始页码
END_PAGE = 50         # 结束页码
DOWNLOAD_DIR = r"C:\Users\13822\.openclaw\workspace\gokifu_sgf"  # 棋谱保存文件夹
DELAY_SECONDS = 3    # 每次请求间隔秒数
# ====================================================================

# 创建保存文件夹
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 请求头（模拟浏览器，防止被简单拦截）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

def test():
    print("HELLO!")
    return

def download_sgf(game_id, dir, cur_num, total_num):
    """下载单个棋谱SGF文件"""
    sgf_url = f"http://gokifu.com/f/{game_id}.sgf"
    file_path = os.path.join(dir, f"{game_id}.sgf")

    # 跳过已下载的文件
    if os.path.exists(file_path):
        print(f"✅ 已存在：{game_id}.sgf")
        return True

    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(sgf_url, headers=headers, timeout=20)
        response.raise_for_status()  # 请求失败抛出异常

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"📥 下载成功：{game_id}.sgf {cur_num}/{total_num}" )
        time.sleep(random.uniform(DELAY_SECONDS-1, DELAY_SECONDS+1))
        return True

    except Exception as e:
        print(f"❌ 下载失败 {game_id}：{str(e)}")
        return False

def get_game_ids_from_page(page, year, month):
    """从列表页获取所有对局ID"""
    url = f"http://gokifu.com/index.php?p={page}&a=1&y={year}&m={month}"
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        # 提取所有 /s/xxxx 格式的对局链接
        game_ids = []
        for a in soup.select("a[href^='http://gokifu.com/share/']"):
            href = a.get("href")
            # 提取ID：/s/abc123 → abc123
            game_id = href.replace("http://gokifu.com/share/", "")
            game_ids.append(game_id)

        print(f"\n📄 {year}年{month}月 第 {page} 页 找到 {len(game_ids)} 个对局")
        time.sleep(DELAY_SECONDS)
        return game_ids

    except Exception as e:
        print(f"❌ 获取第 {page} 页失败：{str(e)}")
        #sys.exit()
        return []

def main():
    print("=" * 50)
    print("GoKifu 围棋棋谱批量下载器（仅个人学习使用）")
    print(f"延时：{DELAY_SECONDS} 秒 | 保存到：{DOWNLOAD_DIR}")
    print("=" * 50)
    print()

    total_success = 0
    # 逐年爬取
    for year in range(START_YEAR, END_YEAR+1):
        year_dir = os.path.join(DOWNLOAD_DIR, str(year))
        # 逐月爬取
        for month in range(START_MONTH, END_MONTH+1):
            month_str = str(month)
            if month <= 9:
                month_str = '0' + month_str
            month_dir = os .path.join(year_dir, month_str)
            if not os.path.exists(month_dir):
                os.makedirs(month_dir)
            tmp = 0
            # 逐页爬取
            for page in range(START_PAGE, END_PAGE + 1):
                game_ids = []
                while 1:
                    game_ids = get_game_ids_from_page(page, year, month)
                    tmp = len(game_ids)
                    if tmp > 0: break
                    else:
                        time.sleep(30) 
                        continue
                # 逐个下载
                i = 0
                for gid in game_ids:
                    i += 1
                    while 1:
                        if download_sgf(gid, month_dir, i, tmp):
                            total_success += 1
                            break
                        else: continue
                # 隔五页停30秒
                if page%5 == 0:
                    time.sleep(30)
                # 若这一页不足20局，则直接进入下一月
                if tmp < 20 : break

            if tmp < 20: continue
                
        # 每年读取完停1分钟
        time.sleep(60)
    print("\n" + "=" * 50)
    print(f"✅ 任务完成！总计成功下载：{total_success} 个棋谱")
    print("⚠️  仅限个人学习，禁止商用/公开传播！")
    print("=" * 50)

if __name__ == "__main__":
    main()