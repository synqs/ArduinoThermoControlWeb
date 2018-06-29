import os
import eventlet
import numpy as np;
import imageio
from datetime import datetime
from app import db, socketio

cameras = [];
workers = [];
def do_work(cam_id):
    """
    do work and emit message
    """
    print('start it')
    previous_img_files = set()
    cam = Camera.query.get(int(cam_id));
    while cam.switch:
        print('looking')
        img_files = set(os.path.join(cam.folder, f) for f in os.listdir(cam.folder) if f.endswith('.BMP'))
        new_img_files = img_files.difference(previous_img_files)
        if new_img_files:
            timestamp = datetime.now().replace(microsecond=0).isoformat();
            for img_file in new_img_files:
                n_img = imageio.imread(img_file);

                im_crop = n_img[cam.yMin:cam.yMax,cam.xMin:cam.xMax];
                Nat = int(im_crop.sum());
            socketio.emit('camera_response',
                {'time':timestamp, 'data': n_img.tolist(), 'count': cam.unit_of_work,
                'id': cam.id, 'Nat': Nat, 'xmin': cam.xMin, 'xmax': cam.xMax,
                'ymin':cam.yMin, 'ymax':cam.yMax})

            previous_img_files = img_files;

        eventlet.sleep(5)

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True);
    switch = db.Column(db.Boolean)
    unit_of_work = db.Column(db.Integer)
    name = db.Column(db.String(64))
    ard_str = db.Column(db.String(120))
    folder = db.Column(db.String(240))
    xMin = db.Column(db.Integer)
    xMax = db.Column(db.Integer)
    yMin = db.Column(db.Integer)
    yMax = db.Column(db.Integer)

    def __repr__(self):
        return '<Camera {}>'.format(self.name)

    def is_open(self):
        '''
        test if the worker is running
        '''
        return self.switch

    def label(self):
        return 'read_camera' + str(self.id);

    def start(self):
        """
        start to listen to the serial port of the Arduino
        """
        print('Starting the listener.')
        if not self.switch:
            self.switch = True
            db.session.commit()
            thread = socketio.start_background_task(target=do_work, cam_id = self.id);
            print(thread.name);
            print(vars(thread));
            print(thread.ident);
            workers.append(thread);
        else:
            print('Already running')

class GuppySocketProtocol(object):
    '''
    A class which combines the serial connection and the socket into a single
    class, such that we can handle these things more properly.
    '''

    id = 0;
    switch = False
    unit_of_work = 0
    name = '';
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
                self.socketio.emit('camera_response',
                    {'time':timestamp, 'data': n_img.tolist(), 'count': self.unit_of_work,
                    'id': self.id, 'Nat': Nat, 'xmin': self.xMin, 'xmax': self.xMax,
                    'ymin':self.yMin, 'ymax':self.yMax})

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
