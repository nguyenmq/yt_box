import select
import socket

hostname = "localhost"
port= 9000

listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen.bind( (hostname, port) )
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
        else:
            data = sock.recv(1024)
            if data:
                print(data)
            else:
                inputs.remove(sock)
