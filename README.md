# Lianjia
 
主要文件为 spiders文件夹下的 chengjiao_aria.py //其他均未通过测试

## 环境准备
1. python: [下载anaconda并安装](https://docs.anaconda.com/anaconda/install/windows/)
2. pycharm：下载pycharm 安装就好

3. 下载本项目
用pycharm 打开项目（可以直接在包含这个项目的文件夹

***可能需要的环境文件***
scrapy 和依赖安装： 打开anaconda powershell 输入
```
conda install -c conda-forge scrapy
conda install -c conda-forge requests
conda install -c conda-forge lxml
conda install -c conda-forge beautifulsoup4
```
Random user agent 组件
https://github.com/alecxe/scrapy-fake-useragent

## 使用
1.首先注意改chengjiao_aria.py 的第31行，其中的 i 代表城市列表中的第几行
![0060133c224286bdb0d9a928cf47bd10.png](https://github.com/sqyqyq/Lianjia/blob/master/img/city_list.png)

建议先使用 i = 2，也就是先采北京，如果北京没问题那其他也应该没问题

2. 修改middlewares 文件中的 api （我这里使用的是代理云api）
 ![cf24aa7b01cb2fc4d96ae3afebe0b1cd.png](https://github.com/sqyqyq/Lianjia/blob/master/img/api.png)
 
3. 在terminal 中使用以下代码运行
 `scrapy crawl chengjiao_aria.py`
 更多教程在官方文档 https://docs.scrapy.org/en/latest/intro/tutorial.html
 
 
## 其他文件介绍
1. log： log文件用来记录过程来debug的，运行过程中一些流程也会在terminal中打印出来。
`logging.warning('delete wrong')`
2. check：check 文件用来获取能爬取到的最早的日期，用来检测是否有爬不到的日期
3. stat： stat 文件用来计算能爬到的数量

* * *

## 此项目涉及的点（方便以后参考）
custompolicy.py: http_cache policy 加入‘refresh-cache’ 在 mata 里
logger.py: loggerformater 不让scrapy老打印或者log 成功的item
用切割价格和面积 以获得更多链家信息
自定义 middleware 使用 代理云 ip 
使用 fake user agent
