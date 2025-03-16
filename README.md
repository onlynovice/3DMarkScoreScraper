# 3DMark跑分爬取工具 3DMarkScoreScraper

## 要求 Requirements
Python >= 3.9

## 依赖 Dependencies
openpyxl, tqdm, pandas, requests, tenacity, questionary

## 用法 Usage
```python
git clone https://github.com/fakepheonix/3DMarkScoreScraper.git
python Main.py
```

## 说明 Description
获取3DMark跑分数据，可以获取显卡/CPU的多种场景下的平均跑分。
- CPU数据来源：3DMark CPU Profile
- GPU数据来源：3DMark Time Spy, Time Spy Extreme, Port Royal, Steel Nomad
支持设定一段时间（如5天），获取这段天数之前至今的平均分（如从5天前到今天）

[3DMark Search](https://www.3dmark.com/search?#advanced?test=spy%20P&cpuId=&gpuId=1509&gpuCount=1&gpuType=ALL&deviceType=ALL&storageModel=ALL&showRamDisks=false&memoryChannels=0&country=&scoreType=graphicsScore&hofMode=true&showInvalidResults=false&freeParams=&minGpuCoreClock=&maxGpuCoreClock=&minGpuMemClock=&maxGpuMemClock=&minCpuClock=&maxCpuClock=)

有两种模式
1. 全量更新，从3dmark爬取数据，保存到本地（json格式），然后处理数据导出Excel
2. 从本地读取json数据，处理数据导出Excel
