from app import app, socketio
from app.cameracontrol.forms import UpdateForm, ConnectForm, RoiForm
from app.cameracontrol import bp
from app.cameracontrol.models import GuppySocketProtocol, cameras
import h5py

from flask import render_template, flash, redirect, url_for, session
from flask_socketio import emit, disconnect

@bp.route('/camera_details/<ard_nr>', methods=['GET', 'POST'])
def camera_details(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    global cameras;
    if not cameras:
        flash('No cameras installed', 'error')
        return redirect(url_for('main.index'))

    n_ards = len(cameras);

    arduino = cameras[int(ard_nr)];
    n_ards = len(cameras);
    props = [];
    for ii, arduino in enumerate(cameras):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'folder': arduino.folder,
        'active': arduino.is_open(), 'label': temp_field_str, 'xmin':arduino.xMin,
        'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};
        props.append(dict)

    name = arduino.name;
    folder = arduino.folder;
    conn_open = arduino.is_open()
    return render_template('camera_details.html',n_ards = n_ards, props = props, ard_nr = ard_nr,
        name = name, conn_open = conn_open);

@bp.route('/add_camera', methods=['GET', 'POST'])
def add_camera():
    '''
    Add a camera to the set up
    '''
    global cameras;
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_folder =  cform.folder.data;
        name = cform.name.data;
        camera = GuppySocketProtocol(socketio, n_folder, name);
        camera.id = len(cameras)
        try:
            camera.start();
            cameras.append(camera)
            return redirect(url_for('main.index'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('cameracontrol.add_camera'))

    folder = app.config['CAMERA_FOLDER']
    n_ards = len(cameras)
    return render_template('add_camera.html', folder = folder, cform = cform, n_ards=n_ards);

@bp.route('/change_camera/<ard_nr>')
def change_camera(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    global cameras;
    if not cameras:
        flash('No cameras installed', 'error')
        return redirect(url_for('cameracontrol.add_camera'))

    n_ards = len(cameras);
    arduino = cameras[int(ard_nr)];
    props = {'name': arduino.name, 'id': int(ard_nr), 'folder': arduino.folder,
            'active': arduino.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

    uform = UpdateForm(id=ard_nr)
    roi_form = RoiForm(id=ard_nr)
    return render_template('change_camera.html',
        form=uform, roi_form = roi_form, props=props);

@bp.route('/update', methods=['POST'])
def update():
    '''
    Update the watched folder.
    '''
    global cameras
    if not cameras:
        flash('No camera yet.', 'error')
        return redirect(url_for('add_camera'))

    uform = UpdateForm();
    roi_form = RoiForm();

    id = int(uform.id.data);
    camera = cameras[id];

    if uform.validate_on_submit():

        camera = cameras[int(id)];
        n_folder =  uform.folder.data;
        if os.path.isdir(n_folder):
            camera.folder = n_folder;
            flash('Updated the folder to {}'.format(n_folder))
        else:
            flash('Folder does not exist', 'error');
        return redirect(url_for('cameracontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': camera.name, 'id': int(ard_nr), 'folder': camera.folder,
            'active': camera.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

        return render_template('change_camera.html', form=uform, roi_form= roi_form, props=props);

@bp.route('/roi', methods=['POST'])
def roi():
    '''
    Update the roi.
    '''
    global cameras
    if not cameras:
        flash('No camera yet.', 'error')
        return redirect(url_for('add_camera'))

    uform = UpdateForm();
    roi_form = RoiForm();

    id = int(roi_form.id.data);
    camera = cameras[id];

    if roi_form.validate_on_submit():

        camera = cameras[int(id)];
        camera.xMin = roi_form.xMin.data;
        camera.xMax = roi_form.xMax.data;
        camera.yMin = roi_form.yMin.data;
        camera.yMax = roi_form.yMax.data;
        flash('Updated the camera ROI');
        return redirect(url_for('cameracontrol.change_camera', ard_nr = id))
    else:
        props = {'name': camera.name, 'id': int(ard_nr), 'folder': camera.folder,
            'active': camera.is_open(), 'xmin':arduino.xMin,
            'xmax':arduino.xMax, 'ymin':arduino.yMin, 'ymax':arduino.yMax};

        return render_template('change_camera.html', form=uform, roi_form= roi_form, props=props);

@bp.route('/file/<filestring>')
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

    global cameras;

    if id >= len(cameras):
        flash('Arduino Index out of range.')
        return redirect(url_for('index'))

    arduino = cameras[id];
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

    global cameras;
    # we should even kill the arduino properly.
    if cameras:
        ssProto = cameras[0];
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
    global cameras;
    if cameras:
        arduino = cameras[0];
        arduino.trig_measurement();
        ard_str = 'Triggered a test img.';
    else:
        ard_str = 'Nothing to connect to';

    session['receive_count'] = session.get('receive_count', 0) + 1;
    emit('my_response',
        {'data': ard_str, 'count': session['receive_count']})
