FROM jitesoft/tesseract-ocr

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
RUN apt install python3.8

# install requirements
RUN pip install -r requirements.txt
