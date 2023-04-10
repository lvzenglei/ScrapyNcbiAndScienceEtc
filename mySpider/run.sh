echo 'Scrapy Process Running'
if python /app/mySpider/main.py && python /app/mySpider/doi_main.py; then
  echo 'Scrapy Successfully!!!!!'
else
  echo 'Scrapy Failed!!!!!'
fi