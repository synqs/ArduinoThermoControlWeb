import serial
import eventlet
from datetime import datetime
from app import db, socketio

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
            print('Serial closed')
            tc.switch = False
            db.session.commit()
            # TODO: Make this a link
            error_str = 'Port closed. please configure one properly under config.'
            socketio.emit('log_response',
            {'data': error_str, 'count': unit_of_work})

            # important to use eventlet's sleep method

        eventlet.sleep(sleeptime)
        tc = TempControl.query.get(int(id));
    else:
        print('Closing down the worker in a controlled way.')

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

    def get_serial(self):
        for s in serials:
            if s.port == self.serial_port:
                return s
        return None

    def open_serial(self):
        """
        open the serial port
        """
        s = self.get_serial();
        if s:
            s.open();
        else:
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
        # opening the serial
        if not self.is_open():
            s = self.open_serial();

        # configure the serial

        # starting the listener
        if not self.is_alive():
            self.switch = True
            db.session.commit();
            thread = socketio.start_background_task(target=do_work, id = self.id);
            self.thread_id = thread.ident;
            db.session.commit()
            workers.append(thread);
        else:
            print('Already running')

    def stop(self):
        """
        stop the connection
        """
        for s in serials:
            if s.port == self.serial_port:
                if s.is_open:
                    s.close();
        self.switch = False;
        db.session.commit();
        for ii, t in enumerate(workers):
            if t.ident == self.thread_id:
                del workers[ii];
        return s.is_open

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
