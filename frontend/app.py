#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------
import sys

sys.path.append('..')
from flask import Flask, render_template, request, session, redirect, url_for
from yt_controller import yt_controller
from lib.yt_config import yt_config

config = yt_config()

ytc = yt_controller(config.host, config.port)
application = Flask(__name__)

application.secret_key = config.secret_key

@application.route('/')
def index():
    if 'username' in session:
        username = session['username']
    else:
        return redirect(url_for('login'))

    now_playing = ytc.get_now_playing()
    queue = ytc.get_queue()
    return render_template('index.html', name=now_playing.name, id=now_playing.id, username=now_playing.username, q_count=len(queue), queue=queue, user=username)

@application.route('/add', methods=['POST'])
def add():
    if 'username' in session and request.method == 'POST':
        ytc.add_song(request.form['submit_box'], session['username'])
        return "Success"
    else:
        return "Error"

@application.route('/queue', methods=['GET'])
def queue():
    if 'username' in session and request.method == 'GET':
        new_queue = ytc.get_queue()
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue))
    else:
        return "Error"

@application.route('/now_playing', methods=['GET'])
def now_playing():
    if 'username' in session and request.method == 'GET':
        now_playing = ytc.get_now_playing()
        return render_template('now_playing.html', name=now_playing.name, id=now_playing.id, username=now_playing.username )
    else:
        return "Error"

@application.route('/login', methods=['GET', 'POST'])
def login():
    retry = False
    if request.method == 'POST':
        if len(request.form['submit_box']) > 0:
            session['username'] = request.form['submit_box']
            return redirect(url_for('index'))
        else:
            retry = True

    return render_template('login.html', retry=retry )

@application.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
