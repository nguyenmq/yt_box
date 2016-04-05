#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------

from flask import Flask, render_template, request
from yt_controller import yt_controller

ytc = yt_controller('/tmp/yt_player')
application = Flask(__name__)

@application.route('/')
def index():
    now_playing = ytc.get_now_playing()
    queue = ytc.get_queue()
    return render_template('index.html', name=now_playing[0], id=now_playing[1], q_count=len(queue), queue=queue)

@application.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        new_queue = ytc.add_song(request.form['link'])
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue))
    else:
        return "Error"

@application.route('/queue', methods=['GET'])
def queue():
    if request.method == 'GET':
        new_queue = ytc.get_queue()
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue))
    else:
        return "Error"

@application.route('/now_playing', methods=['GET'])
def now_playing():
    if request.method == 'GET':
        now_playing = ytc.get_now_playing()
        return render_template('now_playing.html', name=now_playing[0], id=now_playing[1] )
    else:
        return "Error"

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
