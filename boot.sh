#!/bin/sh
source venv/bin/activate
flask db upgrade
exec gunicorn -b :5000 --worker-class eventlet -w 1 devicecontrolserver:app
