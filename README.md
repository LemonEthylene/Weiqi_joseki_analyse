# 围棋SAI的出现对围棋定式结构的影响

### ✍️本代码库用于存放用于2026年春“写作与沟通-结构”课程论文在数据分析中所使用的代码和部分分析结果

### ✅建议配合[weiqi-joseki围棋定式数据库](https:////llmbase.ai/openclaw/weiqi-joseki/)和[gokifu.com棋谱网站](http://www.gokifu.com/)食用

### 📜文件内容：

download.py：批量爬取gokifu.com网站上的公开棋谱数据；

analyse.py：批量调用weiqi-joseki数据库中现有代码命令行提取统计某一年的定式数据；

main.py：指定需要分析的年份数据并保存结果为.csv和.json格式；

figure.py：根据结果生成折线统计图；

go_opening_freq_trend.png：2006年至2026年定式使用频率统计结果；

results：存放含统计结果的各.csv和.json文件。

