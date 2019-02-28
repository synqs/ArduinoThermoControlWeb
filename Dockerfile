FROM python:3.6-alpine

RUN adduser -D devicecontrolserver

WORKDIR /home/devicecontrolserver

COPY requirements.txt requirements.txt
RUN apk update
RUN apk add gcc
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY devicecontrolserver.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP devicecontrolserver.py

RUN chown -R devicecontrolserver:devicecontrolserver ./
USER devicecontrolserver

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
