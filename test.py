import flask
import time
import serial

app = flask.Flask(__name__)
#arduino_serial = serial.Serial('/dev/ttyACM0', 9600)
arduino_serial = serial.Serial('/dev/cu.usbmodem1411', 9600)

def event_stream():
    while True:
        time.sleep(5)
        #yield "data: " + arduino_serial.readline() + "\n\n"
        yield "data: \n\n"

@app.route('/stream')
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>

    <script>
        (function(){
            var source = new EventSource('/stream');
            var data = document.getElementById('data');
            source.onmessage = function(e) {
                data.innerHTML = e.data + '
                <p>Test</p><br/>' + data.innerHTML;
            };
        })();
    </script>
    </head>
    <body>
        <title>Arduino serial monitor</title>
        <p>Test</p>
        <div id="data"></div>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run()
#    app.run(debug = True)
