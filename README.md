# ScrapyNcbiAndScienceEtc
使用Scrapy + Selenium + ChromeDriver + Chrome 爬取NCBI Nature Science Cell等网站文献
# 使用Dockerfile创建 scrapy镜像
```
docker build -t scrapy_paper:1.0.4 .
```
# 修改使用在env中的ScrapyProxy变量[不带http://] 
# docker-compose 启动 容器，自动爬取
```
docker-compose -f docker-compose.yaml up -d 
```
# 系统会自动爬取NCBI Science Nature Cell Circulation 一周内的单细胞文献
