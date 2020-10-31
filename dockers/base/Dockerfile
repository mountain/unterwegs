FROM python:3.8-buster
WORKDIR /
RUN apt-get install apt
RUN apt-get update
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
