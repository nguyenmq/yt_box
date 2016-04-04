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
    return render_template('index.html', playing=now_playing[0], q_count=len(queue), queue=queue)

@application.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        new_queue = ytc.add_song(request.form['link'])
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue))

    return "Error"

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
