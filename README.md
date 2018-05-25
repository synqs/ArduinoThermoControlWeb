# ArduinoThermoControlWeb

A flask server that should simplify the logging of our temp control. The website assumes that the Arduino is connected via a serial device. For the moment we have to following abilities:
- It shows data in a long list for the moment.
- It is possible to save the values to an hdf5 file.

On the technical side we use the following ingredients:
- Communication with the Arduino is done through the Serial interface.
- Updates are done through flask_socketio
- The layout is made nice through flask_bootstrap.

The project should serve as a boilerplate for our other sensors too.

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
 start another terminal, and run the _simSerialPort.py_ file through 'python simSerialPort.py'

## Saving to hdf5

We can save the last data to an hdf5 file by calling the _'file/FNAME.h5'_. It  is assumed that the file is already created. Most likely from some program from the  [labscriptsuite](www.labscript.org) or our _NaLi_ control system. An example for calling it from matlab is found in _matlabPythonComm.m_ .

# TODO

 1. Plots and nicer table ?
 2. Error logger to communicate with slack or via email.
 3. Allow for changing the parameters of the feedback loop through some serial communication.
