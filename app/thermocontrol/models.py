import serial
import eventlet
from datetime import datetime
#from app.main.models import User

from app import db, socketio, ma
import time
import requests
from requests.exceptions import ConnectionError
from flask import current_app
import os

workers = [];
serials = [];

def do_work(id, app):
    """
    do work and emit message
    """
    with app.app_context():
        tc = TempControl.query.get(int(id));
        if not tc.sleeptime:
            sleeptime = 3;
        else:
            sleeptime = tc.sleeptime;

        unit_of_work = 0;
        while tc.switch:
            unit_of_work += 1
            # must call emit from the socketio
            # must specify the namespace

            if tc.is_open():
                try:
                    timestamp, ard_str = tc.pull_data()
                    vals = ard_str.split(',');
                    if len(vals)>=2:
                        socketio.emit('temp_value',
                            {'data': vals[1], 'id': id})

                    socketio.emit('log_response',
                    {'time':timestamp, 'data': vals, 'count': unit_of_work,
                        'id': id})
                except Exception as e:
                    print('{}'.format(e))
                    socketio.emit('my_response',
                    {'data': '{}'.format(e), 'count': unit_of_work})
                    tc.switch = False
                    db.session.commit()
            else:
                print('Serial closed')
                tc.switch = False
                db.session.commit()
                # TODO: Make this a link
                error_str = 'Port closed. please configure one properly under config.'
                socketio.emit('log_response',
                {'data': error_str, 'count': unit_of_work})

                socketio.emit('close_conn',{'data': tc.conn_str()});
                # important to use eventlet's sleep method

            eventlet.sleep(sleeptime)
            tc = TempControl.query.get(int(id));
            sleeptime = tc.sleeptime;
        else:
            print('Closing down the worker in a controlled way.')

def do_web_work(id, app):
    """
    do work and emit message
    """
    with app.app_context():
        tc = WebTempControl.query.get(int(id));
        if not tc.sleeptime:
            sleeptime = 3;
        else:
            sleeptime = tc.sleeptime;

        unit_of_work = 0;
        while tc.switch:
            unit_of_work += 1
            # must call emit from the socketio
            # must specify the namespace

            if tc.is_open():
                try:
                    timestamp, ard_str = tc.pull_data()
                    if timestamp:
                        vals = ard_str.split(',');
                    else:
                        vals =[];
                    if len(vals)>=2:
                        socketio.emit('wtemp_value',
                            {'data': vals[1], 'id': id})

                    socketio.emit('wlog_response',
                    {'time':timestamp, 'data': vals, 'count': unit_of_work,
                        'id': id})
                except Exception as e:
                    print('{}'.format(e))
                    socketio.emit('my_response',
                    {'data': '{}'.format(e), 'count': unit_of_work})
                    tc.switch = False
                    db.session.commit()
            else:
                print('Connection closed')
                tc.switch = False
                db.session.commit()
                # TODO: Make this a link
                error_str = 'Port closed. please configure one properly under config.'
                socketio.emit('log_response',
                {'data': error_str, 'count': unit_of_work})

                # important to use eventlet's sleep method

            eventlet.sleep(sleeptime)
            tc = WebTempControl.query.get(int(id));
            sleeptime = tc.sleeptime;
        else:
            print('Closing down the worker in a controlled way.')

class DeviceClass(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True);
    thread_str = db.Column(db.String(120));
    thread_id = db.Column(db.BigInteger, unique=True);
    switch = db.Column(db.Boolean);
    name = db.Column(db.String(64));
    ard_str = db.Column(db.String(120));
    sleeptime = db.Column(db.Float);

class WebTempControl(DeviceClass):
    ip_adress = db.Column(db.String(64));
    port = db.Column(db.String(64));
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'));

    setpoint = db.Column(db.Float);
    gain = db.Column(db.Float);
    integral = db.Column(db.Float);
    diff = db.Column(db.Float);
    value = db.Column(db.Float);

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

    def is_alive(self):
        """
        return the running status
        """
        for thread in workers:
            if str(thread.ident) == self.thread_str:
                self.switch = thread.is_alive();
                db.session.commit();
                return self.switch;

        self.switch = False;
        db.session.commit();
        return self.switch;

    def pull_data(self):
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
        if len(vals)>=2:
            self.value = vals[1]
        else:
            self.value = 0

        db.session.commit();
        timestamp = datetime.now().replace(microsecond=0).isoformat();
        return timestamp, self.ard_str

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

        # starting the listener
        if not self.is_alive():
            self.switch = True
            db.session.commit();
            thread = socketio.start_background_task(target=do_web_work, id = self.id, app = current_app._get_current_object());
            self.thread_str = str(thread.ident)
            db.session.commit()
            workers.append(thread);
        else:
            print('Already running')

    def stop(self):
        """
        stop the connection
        """
        self.switch = False;
        db.session.commit();
        for ii, t in enumerate(workers):
            if str(t.ident) == self.thread_str:
                del workers[ii];
        self.thread_str = '';
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
