#FROM jitesoft/tesseract-ocr:4-latest
FROM python:3.8

# set root user
USER root

# set working dir
WORKDIR /app

# install tesseract
RUN apt-get tesseract-ocr

# install extra langs
RUN apt-get tesseract-ocr-eng \
    & apt-get tesseract-ocr-deu \
    & apt-get tesseract-ocr-fra \
    & apt-get tesseract-ocr-rus \
    & apt-get tesseract-ocr-por \
    & apt-get tesseract-ocr-spa \
    & apt-get tesseract-ocr-tha \
    & apt-get tesseract-ocr-tur \
    & apt-get tesseract-ocr-kor \
    & apt-get tesseract-ocr-jpn \
    & apt-get tesseract-ocr-fas \
    & apt-get tesseract-ocr-equ \
    & apt-get tesseract-ocr-osd

# build extra langs from scratch
#RUN train-lang eng --best
#RUN train-lang deu --best
#RUN train-lang fra --best
#RUN train-lang osd --best
#RUN train-lang rus --best
#RUN train-lang por --best
#RUN train-lang spa --best
#RUN train-lang tha --best
#RUN train-lang tur --best
#RUN train-lang kor --best
#RUN train-lang jpn --best
#RUN train-lang fas --best
#RUN train-lang equ --best

# copy extra langs from pretrained github repo
# https://github.com/tesseract-ocr/tessdata_best

# copy over all github repo files
COPY . .

# update apt-get and install some basics
RUN apt-get update
RUN apt-get --yes --force-yes install curl

# install git
RUN apt-get --yes --force-yes install git

# install python
#RUN apt-get --yes --force-yes install python3.8
RUN apt-get --yes --force-yes install python3-pip

# install some python stuff for psycopg2
# https://stackoverflow.com/questions/62715570/failing-to-install-psycopg2-binary-on-new-docker-container
RUN apt-get --yes install libpq-dev gcc

# install requirements
RUN pip install -r requirements.txt
