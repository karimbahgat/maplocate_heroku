#FROM jitesoft/tesseract-ocr:4-latest
FROM python:3.8

# general guideline for heroku+docker+django
# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

# set root user
USER root

# set working dir
WORKDIR /app

# copy over all github repo files
COPY . .

# update apt-get and install some basics
RUN apt-get update
RUN apt-get --yes --force-yes install curl

# download gazetteers data
WORKDIR data
ADD 'https://filedn.com/lvxzpqbRuTkLnAjfFXe7FFu/Gazetteer%20DB/gazetteers%202022-05-30.zip' gazetteers.zip
RUN unzip gazetteers.zip
RUN rm gazetteers.zip
WORKDIR /app

# install git
RUN apt-get --yes --force-yes install git

# install tesseract
RUN apt-get --yes --force-yes install tesseract-ocr

# install extra langs
RUN apt-get --yes --force-yes install tesseract-ocr-all
#RUN apt-get --yes --force-yes install tesseract-ocr-eng
#RUN apt-get --yes --force-yes install tesseract-ocr-deu
#RUN apt-get --yes --force-yes install tesseract-ocr-fra
#RUN apt-get --yes --force-yes install tesseract-ocr-rus
#RUN apt-get --yes --force-yes install tesseract-ocr-por
#RUN apt-get --yes --force-yes install tesseract-ocr-spa
#RUN apt-get --yes --force-yes install tesseract-ocr-tha
#RUN apt-get --yes --force-yes install tesseract-ocr-tur
#RUN apt-get --yes --force-yes install tesseract-ocr-kor
#RUN apt-get --yes --force-yes install tesseract-ocr-jpn
#RUN apt-get --yes --force-yes install tesseract-ocr-fas
#RUN apt-get --yes --force-yes install tesseract-ocr-equ
#RUN apt-get --yes --force-yes install tesseract-ocr-osd

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

# install python
#RUN apt-get --yes --force-yes install python3.8
RUN apt-get --yes --force-yes install python3-pip

# install some python stuff for psycopg2
# https://stackoverflow.com/questions/62715570/failing-to-install-psycopg2-binary-on-new-docker-container
RUN apt-get --yes install libpq-dev gcc

# install requirements
RUN pip install -r requirements.txt
