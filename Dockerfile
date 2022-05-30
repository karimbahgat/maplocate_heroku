#FROM jitesoft/tesseract-ocr:4-latest
FROM python:3.8-slim

# general guideline for heroku+docker+django
# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

# set root user
USER root

# set working dir
WORKDIR /app

# copy over all github repo files
COPY . .

# update apt-get and install req packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    tesseract-ocr \
    tesseract-ocr-all \
    python3-pip

# install requirements
RUN pip install -r requirements.txt

# download gazetteers data
WORKDIR data
ADD 'https://filedn.com/lvxzpqbRuTkLnAjfFXe7FFu/Gazetteer%20DB/gazetteers%202021-12-03.zip' gazetteers.zip
RUN unzip gazetteers.zip
RUN rm gazetteers.zip
