import os, pty
import time
import numpy as np

def test_serial():
    setpoint  = 750;
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print(s_name)
    while True:
        meas = np.random.randint(700, 800)
        err = setpoint - meas;
        control = np.random.randint(10)
        gain =1
        tauI = 100
        tauD = 1
        mode = os.read(master, 1);
        if mode:
            print('mode {}'.format(mode))
            if mode == b'w':
                ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
                ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD) + '\r\n'
                out = ard_str.encode('windows-1252')
                os.write(master, out)
            if mode == b's':
                set = os.read(master, 20);
                setpoint = int(set.decode('windows-1252'));
                print('s{}'.format(setpoint));

            if mode == b's':
                set = os.read(master, 20);
                setpoint = int(set.decode('windows-1252'));
                print('s{}'.format(setpoint));
        time.sleep(0.1)
if __name__=='__main__':
    test_serial()
