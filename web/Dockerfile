FROM python:2.7.12

RUN mkdir -p /usr/src/app/

COPY . /usr/src/app/

ADD requirements.txt /usr/src/app/requirements.txt

WORKDIR /usr/src/app/

RUN pip install -r requirements.txt




