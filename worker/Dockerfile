FROM python:3.9-buster
WORKDIR /worker
COPY requirements.txt requirements.txt
RUN pip3 install  -i https://pypi.douban.com/simple/ -r requirements.txt
COPY . .
CMD ["celery", "-A", "tasks", "worker", "-l", "INFO"]
