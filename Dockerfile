FROM joyzoursky/python-chromedriver:3.9-selenium
ENV http_proxy http://192.168.3.211:8080
ENV https_proxy http://192.168.3.211:8080

RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN chmod -R 777 /app
CMD ["bash", "-c", "/app/mySpider/run.sh"]