FROM unterwegs:base
RUN apt-get install apt
RUN apt-get update
RUN apt-get -y install build-essential python3-dev libmagickwand-dev ghostscript
WORKDIR /worker
COPY requirements.txt requirements.txt
RUN pip3 install -i https://pypi.douban.com/simple/ -r requirements.txt
RUN python3 -m spacy download en_core_web_md
COPY . .
COPY policy.xml /etc/ImageMagick-6/policy.xml
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/bash", "./start.sh"]
