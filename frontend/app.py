#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------
import sys
from datetime import timedelta

sys.path.append('..')
from flask import Flask, render_template, request, session, redirect, url_for, make_response
from yt_controller import yt_controller
from lib.yt_rpc import yt_rpc
from lib.yt_config import yt_config

config = yt_config()

ytc = yt_controller(config.host, config.port)
application = Flask(__name__)

application.secret_key = config.secret_key
application.permanent_session_lifetime = timedelta(days=1)

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

@application.route('/remove', methods=['POST'])
def remove():
    alrt_type = yt_rpc.ALRT_DANGER
    alrt_emph = "Error"
    alrt_msg = "Invalid request to remove video"

    if 'username' in session and 'id' in request.form and request.method == 'POST':
        parsed_json = ytc.remove_song(request.form['id'], session['username'])

        if parsed_json is not None:
            alert = parsed_json['alert']
            alrt_type = alert['type']
            alrt_emph = alert['emph']
            alrt_msg = alert['msg']

    response = make_response(render_template('alert.html', alrt_type=alrt_type, alrt_emph=alrt_emph, alrt_msg=alrt_msg))
    if alrt_type == yt_rpc.ALRT_DANGER:
        response.status = 500

    return response

@application.route('/queue', methods=['GET'])
def queue():
    if 'username' in session and request.method == 'GET':
        new_queue = ytc.get_queue()
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue), user=session['username'])
    else:
        return "Error"

@application.route('/now_playing', methods=['GET'])
def now_playing():
    alrt_type = yt_rpc.ALRT_DANGER
    alrt_emph = "Error"

    if request.method == 'GET':
        if 'username' in session:
            now_playing = ytc.get_now_playing()
            response = make_response(render_template('now_playing.html', name=now_playing.name, id=now_playing.id, username=now_playing.username ))
            response.status_code = 200
            return response
        else:
            alrt_msg = "AJAX request missing a session id"
    else:
        alrt_msg = "Now Playing request requires a GET"

    response = make_response(render_template('alert.html', alrt_type=alrt_type, alrt_emph=alrt_emph, alrt_msg=alrt_msg))
    response.status_code = 500
    return response

@application.route('/login', methods=['GET', 'POST'])
def login():
    alrt_type = None
    alrt_emph = None
    err_msg = None

    if request.method == 'POST':
        if len(request.form['submit_box']) > 0:
            session['username'] = request.form['submit_box']
            session.permanent = True
            return redirect(url_for('index'))
        else:
            alrt_emph = "Error"
            err_msg = "Username can't be blank"
            alrt_type = yt_rpc.ALRT_DANGER

    return render_template('login.html', alrt_type=alrt_type, alrt_emph=alrt_emph, alrt_msg=err_msg)

@application.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
