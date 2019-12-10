from app import create_app
from config import ProductionConfig
socketio, app = create_app(ProductionConfig)

if __name__=='__main__':
    socketio.run(app,host='0.0.0.0', debug=True)
