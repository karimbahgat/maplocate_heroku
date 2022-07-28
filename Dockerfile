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
    unzip \
    git \
    tesseract-ocr \
    tesseract-ocr-all \
    python3-pip

# install requirements
RUN pip install -r requirements.txt

# download mysql gazetteer ssl certificate
WORKDIR data
RUN curl -o azure-mysql-DigiCertGlobalRootCA.crt.pem https://filedn.com/lvxzpqbRuTkLnAjfFXe7FFu/Gazetteer%20DB/azure-mysql-DigiCertGlobalRootCA.crt.pem

# set back to main dir
WORKDIR /app
