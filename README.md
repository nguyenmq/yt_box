## Youtube Jukebox

### Description
A quick way to share videos with people in the same living room. The design
requires one computer hooked up to a computer to act as both the server and
video player. Users log into the served up webpage and can paste Youtube links
to queue them on the server.

### Dependencies

+ Python3
+ Flask
+ nginx
+ uWSGI

### Installation

#### Python Virtual Environement
This serves as the environment for developing `yt_box`

+ Install `virtualenv` from `pip`:
```
sudo pip install virtualenv
```

+ Go to the `frontend` directory:
```
cd <repo location>/yt_box/frontend
```

+ Make a Python virtual environment within the repo:
```
virtualenv appenv
```

+ Activate the virtual environment:
```
source appenv/bin/activate
```

+ Install Flask and uWSGI:
```
pip install flask uwsgi
```

#### Configure uWSGI
+ Use the included uWSGI configuration

#### Configure nginx
+ Use the include nginx configuration

### Running yt_box
+ For development, the Flask server can be used by executing the app from within
  your virtual environment:
```
python app.py
```

+ The uWSGI server can also be used during development:
```
uwsgi --socket 0.0.0.0:8000 --protocol=http -w wsgi
```

+ Using nginx:
```
systemctl start nginx
uwsgi --ini app.ini
```
    + Someday launching uWSGI should go inside a systemd service file

### Design
`yt_box` is split into a frontend Flask application and a backend application
that maintains the video queue and plays the video. The backend acts as a local
socket server that accepts RPC messages from the Flask application formatted in
JSON.
