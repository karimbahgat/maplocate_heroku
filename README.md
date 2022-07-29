# maplocate_heroku
 Maplocate backend on heroku

# Heroku Setup

Requires the following steps when setting up Heroku:
- Set the app to run as a docker container rather than a stack:
  `heroku stack:set container -a appname`
- Build and deploy from this repo.
- Environment variables:
  - SECRET_KEY=[random key to use for django]
  - DATABASE_URL=sqlite:///db.sqlite3 [so django doesn't complain]
  - GEOCODER_HOST=...
  - GEOCODER_PORT=...
  - GEOCODER_DATABASE=...
  - GEOCODER_USER=...
  - GEOCODER_PASSWORD=...