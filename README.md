# ScrapyNcbiAndScienceEtc
使用Scrapy + Selenium + ChromeDriver + Chrome 爬取NCBI Nature Science Cell等网站文献
# 一、linux 环境运行

# 1.1 Dockerfile创建 scrapy镜像
```
docker build -t scrapy_paper:1.0.4 .
```
# 1.2 修改使用在env中的ScrapyProxy变量[不带http://] 
# 1.3 docker-compose 启动 容器，自动爬取
```
docker-compose -f docker-compose.yaml up -d 
```
# 系统会自动爬取NCBI Science Nature Cell Circulation 一周内的单细胞文献

# 二、在window 环境下运行时
## 2.1 需要安装docker desktop window ，并安装WSL2 
- ---[由于上述镜像都是linux环境构建的，所以在window构建及运行时，一定要用wsl模拟linux]
## 2.2 进入git目录，构建镜像启动
```
docker build -t scrapy_paper:1.0.4 .
docker-compose -f docker-compose.yaml up -d 
```
## 2.3 mongo compass 做mongodb的可视化


# To do List 
- Deploying to a Scrapyd Server to control spider
