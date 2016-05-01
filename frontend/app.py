#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------
import sys
import os
from datetime import timedelta

sys.path.append('..')
from flask import Flask, render_template, request, session, redirect, url_for, make_response, send_from_directory
from yt_controller import yt_controller
from lib.yt_rpc import yt_rpc as yt_rpc
from lib.yt_config import yt_config

config = yt_config()
ytc = yt_controller(config.host, config.port)
application = Flask(__name__)

application.secret_key = config.secret_key
application.permanent_session_lifetime = timedelta(days=1)

@application.route('/')
def index():
    if 'user_id' in session:
        username = session['username']
        user_id = session['user_id']
        now_playing = ytc.get_now_playing()
        queue = ytc.get_queue()
        return render_template('index.html', name=now_playing.name,
                    now_playing=now_playing, q_count=len(queue),
                    queue=queue, user=username, user_id=user_id)
    else:
        return redirect(url_for('login'))

@application.route('/add', methods=['POST'])
def add():
    alrt_type = yt_rpc.ALRT_DANGER
    alrt_emph = "Error"
    alrt_msg = "Invalid request to add video"
    status = False

    if 'user_id' in session and request.method == 'POST':
        parsed_rsp = ytc.add_song(request.form['submit_box'], session['user_id'])

        if parsed_rsp is not None:
            alrt_type, alrt_emph, alrt_msg = yt_rpc.unpack_alert(parsed_rsp['alert'])
            status = parsed_rsp['status']

    response = make_response(render_template('alert.html', alrt_type=alrt_type,
                                    alrt_emph=alrt_emph, alrt_msg=alrt_msg))
    if status == False:
        response.status_code = 500

    return response

@application.route('/remove', methods=['POST'])
def remove():
    alrt_type = yt_rpc.ALRT_DANGER
    alrt_emph = "Error"
    alrt_msg = "Invalid request to remove video"
    status = False

    if 'user_id' in session and 'vid_id' in request.form and request.method == 'POST':
        parsed_rsp = ytc.remove_song(request.form['vid_id'], session['user_id'])

        if parsed_rsp is not None:
            alrt_type, alrt_emph, alrt_msg = yt_rpc.unpack_alert(parsed_rsp['alert'])
            status = parsed_rsp['status']

    response = make_response(render_template('alert.html', alrt_type=alrt_type,
                                    alrt_emph=alrt_emph, alrt_msg=alrt_msg))
    if status == False:
        response.status_code = 500

    return response

@application.route('/queue', methods=['GET'])
def queue():
    if 'user_id' in session and request.method == 'GET':
        new_queue = ytc.get_queue()
        return render_template('queue.html', queue=new_queue, q_count=len(new_queue), user_id=session['user_id'])
    else:
        return "Error"

@application.route('/now_playing', methods=['GET'])
def now_playing():
    alrt_type = yt_rpc.ALRT_DANGER
    alrt_emph = "Error"

    if request.method == 'GET':
        if 'user_id' in session:
            now_playing = ytc.get_now_playing()
            response = make_response(render_template('now_playing.html',
                                        now_playing=now_playing, user_id=session['user_id'],
                                        username=now_playing.username ))
            response.status_code = 200
            return response
        else:
            alrt_msg = "AJAX request missing a session id"
    else:
        alrt_msg = "Now Playing request requires a GET"

    response = make_response(render_template('alert.html', alrt_type=alrt_type,
                    alrt_emph=alrt_emph, alrt_msg=alrt_msg))
    response.status_code = 500
    return response

@application.route('/login', methods=['GET', 'POST'])
def login():
    alrt_type = None
    alrt_emph = None
    alrt_msg = None

    if request.method == 'POST':
        if len(request.form['submit_box']) > 0:
            username = request.form['submit_box']
            parsed_rsp = ytc.add_user(username)
            if parsed_rsp['status'] == True:
                session['user_id'] = parsed_rsp['user_id']
                session['username'] = parsed_rsp['username']
                session.permanent = True
            else:
                alrt_type, alrt_emph, alrt_msg = yt_rpc.unpack_alert(parsed_rsp['alert'])
        else:
            alrt_emph = "Error"
            alrt_msg = "Username can't be blank"
            alrt_type = yt_rpc.ALRT_DANGER

    if request.method == 'GET' or alrt_type:
        return render_template('login.html', alrt_type=alrt_type, alrt_emph=alrt_emph, alrt_msg=alrt_msg)
    else:
        return redirect(url_for('index'))

@application.route('/logout')
def logout():
    ytc.remove_user(session['user_id'])
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
