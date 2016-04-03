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
+ youtube_dl

### Installation

#### Python Virtual Environement
This serves as the environment for developing `yt_box`

+ Install `virtualenv` from `pip`:
```
sudo pip install virtualenv
```

+ Go to the repo's directory:
```
cd <repo location>/yt_box/
```

+ Make a Python virtual environment within the repo:
```
virtualenv yt_box_env
```

+ Activate the virtual environment:
```
source yt_box_env/bin/activate
```

+ Install Flask, uWSGI, and youtube_dl:
```
pip install flask uwsgi youtube_dl
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

+ Starting the web services manually:
```
systemctl start nginx
uwsgi --ini app.ini
```

+ Enabling the web services to start at boot:
```
# Because this is being developed on Arch, which uses systemd:
systemctl enable nginx
uwsgi --ini app.ini # There still needs to be a service file written for this part
```

### Design
`yt_box` is split into a frontend Flask application and a backend application
that maintains the video queue and plays the video. The backend acts as a local
socket server that accepts RPC messages from the Flask application formatted in
JSON.
