import os
import select
import socket
import subprocess
import sys

sys.path.append('..')
from yt_player import yt_player
from lib.yt_config import yt_config

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
    quote_cnt = 0
    start = 0
    end = 0

    # Loop through the string. Increment the count when we
    # see an open bracket and decrement on a closing
    # bracket. When the count hits zero, we found the
    # closing bracket of a message
    for i, c in enumerate(messages):
        end = i

        # count the double quotes around strings
        if c is '"' and messages[i - 1] is not '\\':
            quote_cnt = quote_cnt + 1

        # only count the curly brackets when they're not
        # within strings
        if c is '{' and quote_cnt % 2 is 0:
            bracket_cnt = bracket_cnt + 1
        elif c is '}' and quote_cnt % 2 is 0:
            bracket_cnt = bracket_cnt - 1

        if bracket_cnt is 0:
            ytp.parse_msg(sock, messages[start:end+1])
            start = end + 1

    # TODO: deal with partial messages
    # if bracket_cnt is not 0:

#-----------------------------------------------------------
# Start of application
#-----------------------------------------------------------
config = yt_config()

ytp = yt_player()

try:
     os.unlink(config.host)
except OSError:
    if os.path.exists(config.host):
        raise

listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen.bind( (config.host, config.port) )
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
        else:
            data = sock.recv(1024)
            if data:
                extract_msgs(sock, data.decode('utf-8'))
            else:
                sock.close()
                inputs.remove(sock)

    if child:
        return_code = child.poll()
        if return_code is not None:
            playing = False

    if not playing:
        next_video = ytp.get_next_video()
        if next_video:
            print("\nNow Playing: {}\n".format(next_video.name))
            link = "https://www.youtube.com/watch?v={}".format(next_video.id)

            args = [config.player]
            raw_args = str(config.player_args).format(link)
            args.extend(raw_args.split(' '))
            child = subprocess.Popen(args)
            playing = True

