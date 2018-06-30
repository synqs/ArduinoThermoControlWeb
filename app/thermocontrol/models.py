import serial
import eventlet
from datetime import datetime
from app import db, socketio

tempcontrols = [];
workers = [];
serials = [];

def do_work(id):
    """
    do work and emit message
    """

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
            tc.switch = False
            db.session.commit()
            # TODO: Make this a link
            error_str = 'Port closed. please configure one properly under config.'
            socketio.emit('log_response',
            {'data': error_str, 'count': unit_of_work})

            # important to use eventlet's sleep method

        eventlet.sleep(sleeptime)

class TempControl(db.Model):
    id = db.Column(db.Integer, primary_key=True);
    thread_id = db.Column(db.Integer, unique=True);
    switch = db.Column(db.Boolean)
    name = db.Column(db.String(64))
    ard_str = db.Column(db.String(120))

    serial_port = db.Column(db.String(64))
    setpoint = db.Column(db.Float);
    gain = db.Column(db.Float);
    integral = db.Column(db.Float);
    diff = db.Column(db.Float);
    sleeptime = db.Column(db.Float);

    def __repr__(self):
        return '<TempControl {}>'.format(self.name)

    def open_serial(self):
        """
        open the serial port
        """
        for s in serials:
            if s.port == self.serial_port:
                if not s.is_open:
                    s= serial.Serial(self.serial_port, 9600, timeout = 1);
                return s.is_open
        s= serial.Serial(self.serial_port, 9600, timeout = 1);
        serials.append(s);
        return s.is_open

    def update_serial(self, serial_port):
        """
        open the serial port
        """
        self.serial_port = serial_port;
        db.session.commit();

        exists = False
        for s in serials:
            if s.port == serial_port:
                s = serial.Serial(serial_port, 9600, timeout = 1);
                exists = True;

        if not exists:
            s = serial.Serial(serial_port, 9600, timeout = 1);
            serials.append(s);

        return s.is_open

    def connection_open(self):
        '''
        Is the protocol running ?
        '''
        return self.is_alive() and self.is_open()

    def is_open(self):
        '''
        test if the serial connection is open
        '''
        for s in serials:
            if s.port == self.serial_port:
                return s.is_open;
        print('No serial device registered');
        return False

    def is_alive(self):
        """
        return the running status
        """
        for thread in workers:
            if thread.ident == self.thread_id:
                self.switch = thread.is_alive();
                db.session.commit();
                return self.switch;

        self.switch = False;
        db.session.commit();
        return self.switch;

    def temp_field_str(self):
        return 'read' + str(self.id);

    def start(self):
        """
        start to listen to the serial port of the Arduino
        """
        print('Starting the listener.')
        print(self.is_alive())
        if not self.is_alive():
            self.switch = True
            db.session.commit();
            thread = socketio.start_background_task(target=do_work, id = self.id);
            self.thread_id = thread.ident;
            db.session.commit()
            workers.append(thread);
        else:
            print('Already running')

    def pull_data(self):
        '''
        Pulling the actual data from the arduino.
        '''
        ser = [];
        for s in serials:
            if s.port == self.serial_port:
                ser = s;

        # only read out on ask
        o_str = 'w'
        b = o_str.encode()
        ser.write(b);
        stream = ser.read(ser.in_waiting);
        self.ard_str = stream.decode(encoding='windows-1252');
        timestamp = datetime.now().replace(microsecond=0).isoformat();
        return timestamp, self.ard_str

class SerialArduinoTempControl(object):
    '''
    A class which combines the serial connection and the socket into a single
    class, such that we can handle these things more properly.
    '''
    serial = None
    switch = False
    unit_of_work = 0
    name = '';
    id = 0;
    setpoint = '';
    diff = None;
    integral = None;
    gain = None;
    ard_str = '';
    sleeptime = 3;

    def __init__(self, socketio):
        """
        assign socketio object to emit
        """
        self.serial = serial.Serial()
        self.switch = False
        self.socketio = socketio;

    def __init__(self, socketio, name):
        """
        assign socketio object to emit
        """
        self.serial = serial.Serial()
        self.switch = False
        self.socketio = socketio
        self.name = name;

    def is_open(self):
        '''
        test if the serial connection is open
        '''
        return self.serial.is_open

    def is_alive(self):
        """
        return the running status
        """
        return self.switch

    def connection_open(self):
        '''
        Is the protocol running ?
        '''
        return self.is_alive() and self.is_open()

    def stop(self):
        """
        stop the loop and later also the serial port
        """
        self.switch = False
        self.unit_of_work = 0
        if self.is_open():
            self.serial.close()

    def start(self):
        """
        stop the loop and later also the serial port
        """
        if not self.switch:
            if not self.is_open():
                print('the serial port should be open right now')
            else:
                self.switch = True
                thread = self.socketio.start_background_task(target=self.do_work)
        else:
            print('Already running')

    def open_serial(self, port, baud_rate, timeout = 1):
        """
        open the serial port
        """
        self.serial = serial.Serial(port, 9600, timeout = 1)

    def do_work(self):
        """
        do work and emit message
        """

        while self.switch:
            self.unit_of_work += 1

            # must call emit from the socketio
            # must specify the namespace

            if self.is_open():
                try:
                    timestamp, ard_str = self.pull_data()

                    vals = ard_str.split(',');
                    if len(vals)>=2:
                        self.socketio.emit('temp_value',
                            {'data': vals[1], 'id': self.id})

                    self.socketio.emit('log_response',
                    {'time':timestamp, 'data': vals, 'count': self.unit_of_work,
                        'id': self.id})
                except Exception as e:
                    print('{}'.format(e))
                    self.socketio.emit('my_response',
                    {'data': '{}'.format(e), 'count': self.unit_of_work})
                    self.switch = False
            else:
                self.switch = False
                # TODO: Make this a link
                error_str = 'Port closed. please configure one properly under config.'
                self.socketio.emit('log_response',
                {'data': error_str, 'count': self.unit_of_work})

                # important to use eventlet's sleep method
            eventlet.sleep(self.sleeptime)

    def pull_data(self):
        '''
        Pulling the actual data from the arduino.
        '''
        ser = self.serial;
        # only read out on ask
        o_str = 'w'
        b = o_str.encode()
        ser.write(b);
        stream = ser.read(ser.in_waiting);
        self.ard_str = stream.decode(encoding='windows-1252');
        timestamp = datetime.now().replace(microsecond=0).isoformat();
        return timestamp, self.ard_str
