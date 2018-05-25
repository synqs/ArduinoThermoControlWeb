import os, pty
import time
import numpy as np

def test_serial():
    master, slave = pty.openpty()
    s_name = os.ttyname(slave)
    print(s_name)
    while True:
        err = np.random.randint(5)
        meas = np.random.randint(200)
        control = np.random.randint(100)
        ard_str = str(err) + ',' + str(meas) + ',' + str(control) + '\r\n'
        b = ard_str.encode('windows-1252')
        os.write(master, b)
        print('Wrote to master')
        time.sleep(1)
if __name__=='__main__':
    test_serial()
