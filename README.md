# ArduinoMagnetometerWeb

A flask server that should simplify the logging of our temp control. It only shows data for the moment. Should serve as a boilerplate for our other sensors too.

The website assumes that the Arduino is connected via a serial device. 

- Communication with the Arduino is done through the Serial interface.
- Updates are done through flask_socketio
- The layout is made nice through flask_bootstrap.

TODO:

1.) Make the config site look better.
2.) Send the last data to the hdf5 file.
3.) Plots and nicer table ? 

# Installation

- create a new directory
- clone the repository through 'git clone ...' in the new folder
- create a new virtualenv through 'conda create -n YOURNAME python=3.6'
- activate the virtualenv through 'source activate YOURNAME'
- install the dependencies through 'pip install -r requirements.txt'
- start it through 'start.sh'
