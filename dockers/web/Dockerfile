FROM unterwegs:base
WORKDIR /web
ENV FLASK_APP=unterwegs/wsgi.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get install libmagickwand-dev
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]
