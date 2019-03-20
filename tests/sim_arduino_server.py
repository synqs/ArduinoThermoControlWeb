'''
An extremely simple server that might be used for testing the arduino webserver interface.
'''

from flask import Flask, request, jsonify
import numpy as np
app = Flask(__name__)

setpoint = 0;
gain = 0;
tauI = 0;
err = 0;
control = 0;
tauD = 0;

@app.route('/arduino/read/all/')
def get_temp():
    meas = np.random.randint(700, 800);
    global setpoint, gain, tauI, err, control, tauD;
    print(setpoint)
    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

@app.route('/arduino/write/setpoint/<float:n_val>/')
def set_setpoint(n_val):
    global setpoint, gain, tauI, err, control, tauD;
    setpoint = n_val;
    print(setpoint);
    meas = np.random.randint(700, 800);
    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

@app.route('/arduino/write/integral/<float:n_val>/')
def set_integral(n_val):
    global setpoint, gain, tauI, err, control, tauD;
    tauI = n_val;
    print(tauI);
    meas = np.random.randint(700, 800);
    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

@app.route('/arduino/write/differential/<float:n_val>/')
def set_differential(n_val):
    global setpoint, gain, tauI, err, control, tauD;
    tauD = n_val;
    print(tauD);
    meas = np.random.randint(700, 800);
    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

@app.route('/arduino/write/gain/<float:n_val>/')
def set_gain(n_val):
    global setpoint, gain, tauI, err, control, tauD;
    gain = n_val;
    print(gain);
    meas = np.random.randint(700, 800);
    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

if __name__ == '__main__':
    app.run(port=5001, debug=True)
