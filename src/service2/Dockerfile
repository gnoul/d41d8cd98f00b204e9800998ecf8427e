FROM python:3.6

RUN apt-get update && apt-get install -y openssh-server

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
