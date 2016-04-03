import os
import select
import socket
import subprocess
import sys

from yt_player import yt_player

hostname = "/tmp/yt_player"
ytp = yt_player()

try:
    os.unlink( hostname )
except OSError:
    if os.path.exists( hostname ):
        raise

listen = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
listen.bind( hostname )
listen.listen(10)

inputs = [listen]
outputs = []
child = None
playing = False

while inputs:
    readable, writable, errors = select.select(inputs, outputs, inputs, 1)

    for sock in readable:
        if sock is listen:
            connection, client_address = sock.accept()
            connection.setblocking(0)
            inputs.append(connection)
            print( "New connection" )
        else:
            data = sock.recv(1024)
            if data:
                ytp.parse_msg(data.decode('utf-8'))
            else:
                sock.close()
                inputs.remove(sock)
                print( "Removed socket" )

    if child:
        return_code = child.poll()
        if return_code is not None:
            playing = False

    if not playing:
        next_video = ytp.get_next_video()
        if next_video:
            link = "https://www.youtube.com/watch?v={}".format(next_video[1])
            args = ['/usr/bin/mpv', '--fs', link]
            child = subprocess.Popen(args)
            playing = True


