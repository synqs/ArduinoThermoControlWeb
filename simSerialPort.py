import os, pty
import time
import numpy as np

def test_serial():
    setpoint  = 500;
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print(s_name)
    while True:
        meas = np.random.randint(1000)
        err = setpoint - meas;
        control = np.random.randint(100)
        ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control) + '\r\n'
        b = ard_str.encode('windows-1252')
        os.write(master, b)
        print('Wrote to master')
        time.sleep(1)
if __name__=='__main__':
    test_serial()
