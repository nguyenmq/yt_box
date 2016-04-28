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
+ jQuery
+ Bootstrap

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

+ Install the Python dependencies:
```
pip install -r requirements.txt
```

+ Configure yt_box:
```bash
# Make a copy of the sample configuration
cd config
cp yt_box_sample.cfg yt_box.cfg

# Generate a key file for Flask's cookie layer. You can use the command below
# or run your own. The key file must be non-empty.
tr -cd '[:alnum:]' < /dev/urandom | fold -w30 | head -n1 > yt_box.key

# Make any other configuration you may want
```

#### Configure uWSGI:
+ Use the included uWSGI configuration

#### Configure nginx:
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
```bash
systemctl start nginx

# Source the environment and from within the yt_box/backend:
python main.app

# In a new terminal, source the environment, and inside yt_box/frontend:
uwsgi --ini app.ini
```

+ Enabling the web services to start at boot:
```
# Because this is being developed on Arch, which uses systemd:
systemctl enable nginx

# There still needs to be a service file written to start the front and backends
```

### Design
`yt_box` is split into a frontend Flask application and a backend application
that maintains the video queue and plays the video. The backend acts as a local
socket server that accepts RPC messages from the Flask application formatted in
JSON.
