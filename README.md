# multi-user-blog

fsnd: a multi user blog(along the lines of Medium) where users can sign in and post blog posts as well as 'Like' and 'Comment' on other posts made on the blog.

## Setup

- [install google app engine](https://drive.google.com/open?id=0Byu3UemwRffDc21qd3duLW9LMm8)
- create app in [Developer Console](https://console.developers.google.com/)
- run locally `dev_appserver.py .`
- browse locally via [http://localhost:8080](http://localhost:8080)
- set project `gcloud config set project PROJECT_ID`
- deploy app `gcloud app deploy`
- browse app `gcloud app browse`

## Features

- user - signup, login, logout
- post - new, edit, delete, display
- comment - new, delete, edit
- like - add, delete
