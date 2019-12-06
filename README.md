[![Build Status](https://travis-ci.org/synqs/DeviceControlServer.svg?branch=master)](https://travis-ci.org/synqs/DeviceControlServer)

# DeviceControlServer

A flask server that should simplify the logging of our experimental components. Most of the time the components are Arduinos. The website assumes that the Arduinos are connected via ethernet (preferred) or serial. For the moment we have to following abilities:

- Add a few arduinos.
- Give setpoint and live temperature in overview.
- It shows data in a long list for the moment.
- The setpoint can be changed in the config page.
- The data can be exported to csv.
- PID values can be set from the interface.

If you would like to give it a simple test drive, you can access the current build  [on heroku](https://devicecontrolserver.herokuapp.com/).

On the technical side we use the following ingredients:

- Communication is done through ethernet, so we assume an Arduino Yun or something. The code is really mainly tested with the [Yun program here](https://github.com/synqs/YunTemp) or in the ArduinoPrograms folder.
- Communication is still possible with a serial interface. Most likely this will be phased out at some point.
- Updates on the client are done through flask_socketio.
- The layout is made nice through flask_bootstrap.
- Graphics are done with plotly.js

The project serves as a boilerplate for our other sensors too.

Further, we will most likely _never_ install saving of the data on the server as this would make the whole thing MUCH more complicated (where and who to store the data. Which data should we show etc.). A better approach will be to use the devices directly from within BLACS of the labscriptsuite ...

# Installation

## As user
Here it is most likely the best to use the docker image. So install the docker community edition and then get the docker file through:

> docker pull synqs/devicecontrolserver

The next step is to run the file through:

> docker run -p 8000:5000 devicecontrolserver:latest

- open it in a brower on 'localhost:8000'

## For developers

- download github for desktop
- set up the proxy for github
- get mini-conda
- open the anaconda prompt
- set the proxy for anaconda
- create a new directory
- clone the repository through in the new folder through
 > git clone ...
- create a new virtualenv through
 > conda create -n YOURNAME python=3.6
- activate the virtualenv through
> source activate YOURNAME
- install the dependencies through
> pip install -r requirements.txt

 or if you are at the kip:

 > pip --proxy http://proxy.kip.uni-heidelberg.de:8080 install --ignore-installed -r requirements.txt
- set up the database through

> flask db upgrade

- start flask through

> start.sh
- open it in a brower on 'localhost:5000'

# Daily Usage

## Docker

This is the new simplest way, __ but the data will be lost at each update__. You simply run locally after downloading it:

> docker run -p 8000:5000 devicecontrolserver:latest

- open it in a brower on 'localhost:8000'

## The server itself

If you insist on the python approach

 - activate the virtualenv through 'source activate YOURNAME'
 - start it through 'start.sh'
 - runs on 'localhost:5000'

## Test without Arduino

 If you want to test the serial port without having an Arduino, you should just
 start another terminal, and run the _simSerialPort.py_ file through 'python simSerialPort.py'

## Dev updates to the database

If you are changing the properties of the models.py files, it is likely, that you are messing the the tables of the sqlite file in the background of the script. To keep it simple we are using [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/) to keep track. You then have to create the update command through:

> flask db migrate

It creates a new python file in the migrations folder. You then update the sqlite database through a:

> flask db upgrade

# Dev updates to the dockerfile

If you would like to create the dockerfile locally, you might run

>  docker build -t devicecontrolserver:latest .

# TODO

 [x] Allow for changing the parameters of the feedback loop through some serial communication.

 [x] Allow for a cleaner communication between the arduino and flask. Basically, the arduino should only answer to a question be flask.

 [x] Move the information about communications and users into a local database. I think that would make it much more robust.

 [] Allow to change the different axis by hand in the plotly stuff.

 [] Tidy up the connections and also the code in the back-end.

 [] Always make it look cuter.

 [] Error logger to communicate with slack or via email.

 [] make this readme the about page.
