FROM python:3.6-alpine

RUN adduser -D devicecontrolserver

WORKDIR /home/devicecontrolserver

COPY requirements.txt requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev python3-dev
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN apk del .build-deps gcc musl-dev postgresql-dev python3-dev

COPY app app
COPY migrations migrations
COPY devicecontrolserver.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP devicecontrolserver.py

RUN chown -R devicecontrolserver:devicecontrolserver ./
USER devicecontrolserver

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
