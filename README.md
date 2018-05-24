# ArduinoThermoControlWeb

A flask server that should simplify the logging of our temp control. It only shows data for the moment. Should serve as a boilerplate for our other sensors too.

The website assumes that the Arduino is connected via a serial device.

- Communication with the Arduino is done through the Serial interface.
- Updates are done through flask_socketio
- The layout is made nice through flask_bootstrap.

# Installation

- create a new directory
- clone the repository through 'git clone ...' in the new folder
- create a new virtualenv through 'conda create -n YOURNAME python=3.6'
- activate the virtualenv through 'source activate YOURNAME'
- install the dependencies through 'pip install -r requirements.txt'
- start it through 'start.sh'
- open it in a brower on 'localhost:5000'

# Usage

## The server itself
 - activate the virtualenv through 'source activate YOURNAME'
 - start it through 'start.sh'
 - runs on 'localhost:5000'

## Test without Arduino
 If you want to test the serial port without having an Arduino, you should just
 start another terminal, start the python console and run 'import simSerialPort'

# TODO

<<<<<<< HEAD
 1. Verify the connections cleaner.
 2. Send the last data to the hdf5 file.
 3. Plots and nicer table ?
=======
 1. Send the last data to the hdf5 file.
 2. Plots and nicer table ?
 3. Error logger to communicate with slack or via email.
 4. move to gunicorn for work that is not on localhost
>>>>>>> master
