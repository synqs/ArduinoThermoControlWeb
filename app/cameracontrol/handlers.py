from app import app, socketio
from app.cameracontrol.forms import UpdateForm, ConnectForm, RoiForm
import h5py
import git
import os
import numpy as np

import imageio

from flask import render_template, flash, redirect, url_for, session
import time

from flask_socketio import emit, disconnect
import eventlet

# for subplots
import numpy as np
from datetime import datetime

arduinos = [];
ard_str = '';

class GuppySocketProtocol(object):
    '''
    A class which combines the serial connection and the socket into a single
    class, such that we can handle these things more properly.
    '''

    switch = False
    unit_of_work = 0
    name = '';
    id = 0;
    ard_str = '';
    folder = '.';
    xMin = 207; xMax = 597;yMin = 200; yMax = 500;

    def __init__(self, socketio, folder):
        """
        assign socketio object to emit
        add the folder to watch
        """
        if os.path.isdir(folder):
            self.folder = folder;
        else:
            print('Folder does not exist yet.')
            # TODO: Send back an error.
        self.socketio = socketio

    def __init__(self, socketio, folder, name):
        """
        as above, but also assign a name.
        """
        if os.path.isdir(folder):
            self.folder = folder;
        else:
            print('Folder does not exist yet.')
            # TODO: Send back an error.
        self.socketio = socketio;
        self.name = name;

    def is_open(self):
        '''
        test if the worker is running
        '''
        return self.switch

    def stop(self):
        """
        stop the loop and later also the serial port
        """
        self.unit_of_work = 0
        if self.is_open():
            self.serial.close()

    def start(self):
        """
        start to listen to the serial port of the Arduino
        """
        print('Starting the listener.')
        if not self.switch:
            self.switch = True
            thread = self.socketio.start_background_task(target=self.do_work)
        else:
            print('Already running')

    def do_work(self):
        """
        do work and emit message
        """

        previous_img_files = set()
        while self.switch:
            img_files = set(os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.endswith('.BMP'))
            new_img_files = img_files.difference(previous_img_files)
            if new_img_files:
                self.unit_of_work += 1
                timestamp = datetime.now().replace(microsecond=0).isoformat();
                for img_file in new_img_files:
                    n_img = imageio.imread(img_file);

                    im_crop = n_img[self.yMin:self.yMax,self.xMin:self.xMax];
                    Nat = int(im_crop.sum());
                    print(Nat)
                self.socketio.emit('log_response',
                    {'time':timestamp, 'data': n_img.tolist(), 'count': self.unit_of_work,
                    'id': self.id, 'Nat': Nat})

                previous_img_files = img_files;


            eventlet.sleep(0.1)

    def trig_measurement(self):
        '''
        Creating a test pattern in the save_folder.
        '''
        # only read out on ask
        Nx = 752;
        Ny = 578;
        sigma = 20;
        xlin = np.linspace(0,Nx, Nx) - Nx/2;
        ylin = np.linspace(0,Ny, Ny) - Ny/2;
        [X, Y] = np.meshgrid(xlin,ylin);
        z = 255*np.exp(-(X**2 +Y**2)/sigma**2);

        z_int = z.astype('uint8')
        index = np.random.randint(100);
        name = self.folder + '/test' + str(index) + '.BMP';
        print(name)
        imageio.imwrite(name, z_int);

    def pull_data(self):
        '''
        Pulling the actual data from the guppy folder.
        '''
        return timestamp, self.ard_str

@app.context_processor
def git_url():
    '''
    The main function for rendering the principal site.
    '''
    repo = git.Repo(search_parent_directories=True)
    add =repo.remote().url
    add_c = add.split('.git')[0];
    comm = repo.head.object.hexsha;
    return dict(git_url = add_c + '/tree/' + comm);

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''
    global arduinos

    n_ards = len(arduinos);
    props = [];
    for ii, arduino in enumerate(arduinos):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'folder': arduino.folder,
            'active': arduino.is_open(), 'label': temp_field_str, 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};
        props.append(dict)

    return render_template('index.html',n_ards = n_ards, props = props);


@app.route('/details/<ard_nr>', methods=['GET', 'POST'])
def details(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    global arduinos;
    if not arduinos:
        flash('No cameras installed', 'error')
        return redirect(url_for('index'))

    n_ards = len(arduinos);

    arduino = arduinos[int(ard_nr)];
    n_ards = len(arduinos);
    props = [];
    for ii, arduino in enumerate(arduinos):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'folder': arduino.folder,
        'active': arduino.is_open(), 'label': temp_field_str};
        props.append(dict)

    name = arduino.name;
    folder = arduino.folder;
    conn_open = arduino.is_open()
    return render_template('details.html',n_ards = n_ards, props = props, ard_nr = ard_nr,
        name = name, conn_open = conn_open);

@app.route('/add_camera', methods=['GET', 'POST'])
def add_camera():
    '''
    Add a camera to the set up
    '''
    global arduinos;
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_folder =  cform.folder.data;
        name = cform.name.data;
        camera = GuppySocketProtocol(socketio, n_folder, name);
        camera.id = len(arduinos)
        try:
            camera.start();
            arduinos.append(camera)
            return redirect(url_for('index'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('add_camera'))

    folder = app.config['CAMERA_FOLDER']
    n_ards = len(arduinos)
    return render_template('add_camera.html', folder = folder, cform = cform, n_ards=n_ards);

@app.route('/change_arduino/<ard_nr>')
def change_arduino(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    global arduinos;
    if not arduinos:
        flash('No cameras installed', 'error')
        return redirect(url_for('add_camera'))

    n_ards = len(arduinos);
    arduino = arduinos[int(ard_nr)];
    props = {'name': arduino.name, 'id': int(ard_nr), 'folder': arduino.folder,
            'active': arduino.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

    uform = UpdateForm(id=ard_nr)
    roi_form = RoiForm(id=ard_nr)
    return render_template('change_arduino.html',
        form=uform, roi_form = roi_form, props=props);

@app.route('/update', methods=['POST'])
def update():
    '''
    Update the watched folder.
    '''
    global arduinos
    if not arduinos:
        flash('No camera yet.', 'error')
        return redirect(url_for('add_camera'))

    uform = UpdateForm();
    roi_form = RoiForm();

    id = int(uform.id.data);
    camera = arduinos[id];

    if uform.validate_on_submit():

        camera = arduinos[int(id)];
        n_folder =  uform.folder.data;
        if os.path.isdir(n_folder):
            camera.folder = n_folder;
            flash('Updated the folder to {}'.format(n_folder))
        else:
            flash('Folder does not exist', 'error');
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': camera.name, 'id': int(ard_nr), 'folder': camera.folder,
            'active': camera.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

        return render_template('change_arduino.html', form=uform, roi_form= roi_form, props=props);

@app.route('/roi', methods=['POST'])
def roi():
    '''
    Update the roi.
    '''
    global arduinos
    if not arduinos:
        flash('No camera yet.', 'error')
        return redirect(url_for('add_camera'))

    uform = UpdateForm();
    roi_form = RoiForm();

    id = int(roi_form.id.data);
    camera = arduinos[id];

    if roi_form.validate_on_submit():

        camera = arduinos[int(id)];
        camera.xMin = roi_form.xMin.data;
        camera.xMax = roi_form.xMax.data;
        camera.yMin = roi_form.yMin.data;
        camera.yMax = roi_form.yMax.data;
        flash('Updated the camera ROI');
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': camera.name, 'id': int(ard_nr), 'folder': camera.folder,
            'active': camera.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

        return render_template('change_arduino.html', form=uform, roi_form= roi_form, props=props);

@app.route('/file/<filestring>')
def file(filestring):
    '''function to save the values of the hdf5 file. It should have the following structure
    <ard_nr>+<filename>
    '''
    # first let us devide into the right parts
    print(filestring)
    parts = filestring.split('+');
    if not len(parts) == 2:
        flash('The filestring should be of the form')
        return redirect(url_for('index'))

    filename = parts[1]
    id = int(parts[0])

    global arduinos;

    if id >= len(arduinos):
        flash('Arduino Index out of range.')
        return redirect(url_for('index'))

    arduino = arduinos[id];
    # We should add the latest value of the database here. Better would be to trigger the readout.
    # Let us see how this actually works.
    vals = arduino.ard_str.split(' ');
    if vals:
        with h5py.File(filename, "a") as f:
            if 'globals' in f.keys():
                params = f['globals']
                params.attrs['x1'] = np.float(vals[0])
                flash('Added the vals {} to the file {}'.format(arduino.ard_str, filename))
            else:
                flash('The file {} did not have the global group yet.'.format(filename), 'error')
    else:
        flash('Did not have any values to save', 'error')

    return render_template('file.html', file = filename, vals = vals)

# communication with the websocket
@socketio.on('connect')
def run_connect():
    '''
    we are connecting the client to the server. This will only work if the
    Arduino already has a serial connection
    '''
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('stop')
def run_disconnect():
    print('Should disconnect')

    session['receive_count'] = session.get('receive_count', 0) + 1

    global arduinos;
    # we should even kill the arduino properly.
    if arduinos:
        ssProto = arduinos[0];
        ser = ssProto.serial;
        ser.close();
        ssProto.stop();
        emit('my_response',
            {'data': 'Disconnected!', 'count': session['receive_count']})
    else:
        emit('my_response',
            {'data': 'Nothing to disconnect', 'count': session['receive_count']})

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

@socketio.on('trig_img')
def trig_mag():
    global arduinos;
    if arduinos:
        arduino = arduinos[0];
        arduino.trig_measurement();
        ard_str = 'Triggered a test img.';
    else:
        ard_str = 'Nothing to connect to';

    session['receive_count'] = session.get('receive_count', 0) + 1;
    emit('my_response',
        {'data': ard_str, 'count': session['receive_count']})

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
