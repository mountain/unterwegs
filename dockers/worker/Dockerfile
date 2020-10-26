FROM unterwegs:base
WORKDIR /worker
RUN apt-get install libmagickwand-dev
COPY requirements.txt requirements.txt
RUN pip3 install  -i https://pypi.douban.com/simple/ -r requirements.txt
COPY . .
COPY policy.xml /etc/ImageMagick-6/policy.xml
ENTRYPOINT ["/bin/bash", "./start.sh"]
