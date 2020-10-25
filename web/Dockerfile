FROM python:3.9-buster
WORKDIR /web
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
