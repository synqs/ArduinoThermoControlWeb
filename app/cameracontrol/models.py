import os
import eventlet
from datetime import datetime
from app import db

workers = [];

def do_work(cam_id):
    """
    do work and emit message
    """
    previous_img_files = set()
    cam = Camera.query.get(int(cam_id));
    while cam.switch:
        img_files = set(os.path.join(cam.folder, f) for f in os.listdir(cam.folder) if f.endswith('.BMP'))
        new_img_files = img_files.difference(previous_img_files)
        if new_img_files:
            timestamp = datetime.now().replace(microsecond=0).isoformat();
            for img_file in new_img_files:
                n_img = imageio.imread(img_file);

                im_crop = n_img[cam.yMin:cam.yMax,cam.xMin:cam.xMax];
                Nat = int(im_crop.sum());
            socketio.emit('camera_response',
                {'time':timestamp, 'data': n_img.tolist(), 'id': cam.id, 'Nat': Nat,
                'xmin': cam.xMin, 'xmax': cam.xMax, 'ymin':cam.yMin, 'ymax':cam.yMax})

            previous_img_files = img_files;

        eventlet.sleep(1)

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True);
    thread_id = db.Column(db.Integer, unique=True);
    switch = db.Column(db.Boolean)
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
        for thread in workers:
            if thread.ident == self.thread_id:
                self.switch = thread.is_alive();
                db.session.commit();
                return self.switch;

        self.switch = False;
        db.session.commit();
        return self.switch;

    def label(self):
        return 'read_camera' + str(self.id);

    def start(self):
        """
        start to listen to the serial port of the Arduino
        """
        print('Starting the listener.')
        if not self.switch:
            self.switch = True
            db.session.commit();
            thread = socketio.start_background_task(target=do_work, cam_id = self.id);
            self.thread_id = thread.ident;
            db.session.commit()
            workers.append(thread);
        else:
            print('Already running')

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
