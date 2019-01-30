'''
An extremely simple server that might be used for testing the arduino webserver interface.
'''

from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Hey there!"

if __name__ == '__main__':
    app.run(port=5001, debug=True)
