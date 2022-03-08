# maplocate_heroku
 Maplocate backend on heroku

# Heroku Setup

Requires the following steps when setting up Heroku:
- heroku postgresql addon
- heroku-apt buildpack
- heroku stack 18 (20 has an incompatibility with tesseract, see https://stackoverflow.com/questions/66087588/tesseract-error-while-loading-shared-libraries-libarchive-so-13-python)
- environment variables:
  - SECRET_KEY=[random key to use for django]
  - TESSDATA_PREFIX=/app/.apt/usr/share/tesseract-ocr/4.00/tessdata (determined by browsing the heroku app directories)