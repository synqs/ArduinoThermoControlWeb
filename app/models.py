import serial
import eventlet
from datetime import datetime

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
