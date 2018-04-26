FROM python:3.6-alpine

RUN adduser -D ardweb

WORKDIR /home/ardweb

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY arduinomagneto.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP arduinomagneto.py

RUN chown -R ardweb:ardweb ./
USER ardweb

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
