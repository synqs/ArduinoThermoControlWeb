from datetime import datetime
#from app.main.models import User

from app import db, ma
import time
import requests
from requests.exceptions import ConnectionError
from flask import current_app
import os

class WebTempControl(db.Model):
    id = db.Column(db.Integer, primary_key=True); # Not neccessary since id is given automatically ... ?

    switch = db.Column(db.Boolean); # What is this ? = WIT
    name = db.Column(db.String(64));
    ard_str = db.Column(db.String(120)); # WIT
    sleeptime = db.Column(db.Float); # What would be a useful default ?

    ip_adress = db.Column(db.String(64)); # Is there a specific reason to use 64 ?
    port = db.Column(db.String(64));
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'));

    setpoint = db.Column(db.Float);
    value = db.Column(db.Float);
    output = db.Column(db.Float);
    error = db.Column(db.Float);

    gain = db.Column(db.Float);
    integral = db.Column(db.Float);
    diff = db.Column(db.Float);

    timestamp = db.Column(db.DateTime,
        default=datetime.utcnow);

    timeout = 5;

    def __repr__(self):
        ret_str = '<WebTempControl {}'.format(self.name) + ', sleeptime {}>'.format(self.sleeptime)
        return ret_str

    def http_str(self):
        return 'http://' + self.ip_adress + ':' + self.port;

    def temp_http_str(self):
        return self.http_str() + '/arduino/read/all/';

    def temp_field_str(self):
        return 'read_wtc' + str(self.id);

    def conn_str(self):
        return 'conn_wtc' + str(self.id);

    def startstop_str(self):
        return 'start' + str(self.id);

    def connection_open(self):
        '''
        Is the protocol running ?
        '''
        return self.is_alive() and self.is_open()

    def is_open(self):
        '''
        test if the serial connection is open
        '''

        try:
            proxies = {
                'http': None,
                'https': None,
                }
            r = requests.get(self.http_str(), timeout =self.timeout, proxies=proxies);
            return True
        except ConnectionError:
            return False

    def pull_arduino(self):
        '''
        Pulling the actual data from the arduino.
        '''
        try:
            proxies = {
            'http': None,
            'https': None,
            }
            r = requests.get(self.temp_http_str(), timeout =self.timeout, proxies=proxies);
        except ConnectionError:
            print('No connection');
            return 0, 0
        html_text = r.text;
        lines = html_text.split('<br />');
        self.ard_str = lines[1];

        vals = self.ard_str.split(',');
        if len(vals)==7:
            self.setpoint = vals[0];
            self.value = vals[1];
            self.error = vals[2];
            self.output = vals[3];
            self.gain = vals[4];
            self.integral = vals[5];
            sp_vals = vals[6].split('\r');
            self.diff = sp_vals[0];
            self.timestamp = datetime.now().replace(microsecond=0);
            db.session.commit();

    def temp_value(self):
        vals = self.ard_str.split(',');
        if len(vals)>=2:
            return vals[1]
        else:
            return 0


    def start(self):
        """
        start to listen to the serial port of the Arduino
        """
        # test if everything is open
        if not self.is_open():
            print('No connection');
            return

        self.switch = True
        # configure the arduino

        if self.setpoint:
            self.set_setpoint();
        time.sleep(0.2);
        if self.gain:
            self.set_gain();
        time.sleep(0.2);
        if self.integral:
            self.set_integral();
        time.sleep(0.2);
        if self.diff:
            self.set_differential();
        db.session.commit();

    def stop(self):
        """
        stop the connection
        """
        self.switch = False;
        db.session.commit();

    def set_setpoint(self):
        try:
            set_str = '/arduino/write/setpoint/' + str(self.setpoint) + '/';
            addr = self.http_str() + set_str;
            proxies = {
                'http': None,
                'https': None,
                }
            r = requests.get(addr, timeout =self.timeout,proxies=proxies);
            return r.ok;
        except ConnectionError:
            return False

    def set_gain(self):
        try:
            proxies = {
                'http': None,
                'https': None,
                }

            set_str = '/arduino/write/gain/' + str(self.gain) + '/';
            addr = self.http_str() + set_str;
            r = requests.get(addr, timeout = self.timeout,proxies=proxies);
            return r.ok;
        except ConnectionError:
            return False

    def set_integral(self):
        try:
            proxies = {
                'http': None,
                'https': None,
                }
            set_str = '/arduino/write/integral/' + str(self.integral) + '/';
            addr = self.http_str() + set_str;
            r = requests.get(addr, timeout = self.timeout,proxies=proxies);
            return r.ok;
        except ConnectionError:
            return False

    def set_differential(self):
        try:
            proxies = {
                'http': None,
                'https': None,
                }
            set_str = '/arduino/write/differential/' + str(self.diff) + '/';
            addr = self.http_str() + set_str;
            r = requests.get(addr, timeout = self.timeout,proxies=proxies);
            return r.ok;
        except ConnectionError:
            return False

class WtcSchema(ma.ModelSchema):
    class Meta:
        model = WebTempControl

wtc_schema = WtcSchema()
wtcs_schema = WtcSchema(many=True)
