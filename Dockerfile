FROM python:3.6-slim
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y build-essential nginx

RUN mkdir /gh-listener
WORKDIR /gh-listener

COPY requirements.txt /gh-listener/requirements.txt

RUN pip install -r requirements.txt --pre

COPY . /gh-listener
COPY default.nginx.conf /etc/nginx/sites-available/default

EXPOSE 8801
CMD [ "./run.sh" ]
