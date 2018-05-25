import flask

app = flask.Flask(__name__)

def event_stream():
    return 'test\n\n'

@app.route('/stream')
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")

@app.route('/')
def index():
    return """
        <!doctype html>
        <title>Arduino serial monitor</title>
        <div id="data"/>
        <script>
            (function(){
                var source = new EventSource('/stream');
                var data = document.getElementById('data');
                source.onmessage = function(e) {
                    data.innerHTML = e.data + '<br/>' + data.innerHTML;
                };
            })();
        </script>
    """

if __name__ == '__main__':
    app.run(debug = True)
