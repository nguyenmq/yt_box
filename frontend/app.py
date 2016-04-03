#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------

from flask import Flask, render_template, request
from yt_controller import yt_controller

ytc = yt_controller('/tmp/yt_player')
application = Flask(__name__)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        ytc.add_song(request.form['link'])
        return render_template('submit.html')
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        return "error"

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
