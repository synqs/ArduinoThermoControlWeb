'''
An extremely simple server that might be used for testing the arduino webserver interface.
'''

from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def home():
    setpoint = 0;
    
    for el in request.args:
        if el == 's':
            print('Update the setpoint');
            setpoint = float(request.args[el])
            print(setpoint)
    return "setpoint = {} there!".format(setpoint)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
