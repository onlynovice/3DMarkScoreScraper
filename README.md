# 3DMarkScoreScraper

## 要求 Requirements
Python >= 3.9

## 依赖 Dependencies
openpyxl, tqdm, pandas, requests, tenacity, questionary

## 用法 Usage
```python
git clone https://github.com/onlynovice/3DMarkScoreScraper.git
python Main.py
```

## 说明 Description
获取3DMark跑分数据，可以获取显卡/CPU的多种场景下的平均跑分。
- CPU数据来源：3DMark CPU Profile
- GPU数据来源：3DMark Time Spy（图形跑分） & Port Royal（光追跑分）


有两种模式
1. 全量更新，从3dmark爬取数据，保存到本地（json格式），然后处理数据导出Excel
2. 从本地读取json数据，处理数据导出Excel

![image1](Pictures/image1.png)
![image2](Pictures/image2.png)
![image3](Pictures/image3.png)

