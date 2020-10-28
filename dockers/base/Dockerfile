FROM python:3.9-buster
WORKDIR /
RUN apt-get update
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
