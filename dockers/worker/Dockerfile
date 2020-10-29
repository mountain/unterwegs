FROM unterwegs:base
WORKDIR /worker
RUN apt-get -y install build-essential python3-dev libmagickwand-dev ghostscript
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
RUN python3 -m spacy download en_core_web_md
COPY . .
COPY policy.xml /etc/ImageMagick-6/policy.xml
ENTRYPOINT ["/bin/bash", "./start.sh"]
