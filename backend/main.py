import os
import select
import socket
import sys

import yt_player

hostname = "/tmp/yt_player"
ytp = yt_player.yt_player()

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

while inputs:
    readable, writable, errors = select.select(inputs, outputs, inputs)

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

