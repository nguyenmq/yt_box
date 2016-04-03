import os
import select
import socket
import subprocess
import sys

from yt_player import yt_player

def extract_msgs(sock, messages):
    """
    Multiple messages can be received after a recv call on a socket. This
    attempts to extract the individual json messages.

    :param sock: The socket we're currently talking to
    :type sock: socket object

    :param messages: The RPC messages received from the remote client
    :type messages: string
    """
    # some state variables
    bracket_cnt = 0
    start = 0
    end = 0

    # Loop through the string. Increment the count when we
    # see an open bracket and decrement on a closing
    # bracket. When the count hits zero, we found the
    # closing bracket of a message
    for i, c in enumerate(messages):
        end = i
        if c is '{':
            bracket_cnt = bracket_cnt + 1
        elif c is '}':
            bracket_cnt = bracket_cnt - 1

        if bracket_cnt is 0:
            response = ytp.parse_msg(messages[start:end+1])
            if response is not None:
                sock.sendall(response)

            start = end + 1

    # TODO: deal with partial messages
    # if bracket_cnt is not 0:

#-----------------------------------------------------------
# Start of application
#-----------------------------------------------------------
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
                extract_msgs(sock, data.decode('utf-8'))
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

