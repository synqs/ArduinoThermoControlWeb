'''
An extremely simple server that might be used for testing the arduino webserver interface.
'''

from flask import Flask, request, jsonify
import numpy as np
app = Flask(__name__)

@app.route('/')
def home():
    setpoint = 0;
    meas = np.random.randint(700, 800)
    err = 0;
    control = 0;
    gain = 0;
    tauI = 0;
    tauD = 0;

    for el in request.args:
        if el == 's':
            print('Update the setpoint');
            setpoint = float(request.args[el])
            print(setpoint)

    first_line = "setpoint, input, error, output, G, tauI, tauD <br />";
    ard_str = str(setpoint) + ',' + str(meas) + ',' + str(err) + ',' + str(control)
    ard_str = ard_str + ',' + str(gain) + ',' + str(tauI) +',' + str(tauD);

    return first_line + ard_str;

@app.route('/data/temp/')
def get_temp():
    meas = np.random.randint(700, 800);
    rdict = {'value': str(meas), 'key': 'temp', 'response': 'get'}
    return jsonify(rdict);

if __name__ == '__main__':
    app.run(port=5001, debug=True)
