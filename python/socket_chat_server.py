# -*- coding: utf-8 -*-
"""
This is a simple example of socket module
"""
import socket
import select
import re

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(1)

    clients = [sock]
    auth_clients = {}

    while 1:
        read = select.select(clients, [], [], 2)[0]

        if not read:
            continue

        if sock in read:
            new_sock = sock.accept()[0]
            clients.append(new_sock)
            new_sock.send("This simple chat server. Type 'iam:username' for authorize!\n")

            print "There are %s client(s) connected to the server" % (len(clients) -1)
            read.remove(sock)

        for read_sock in read:
            data = read_sock.recv(1024)
            if not data:
                print "Client disconected!"
                clients.remove(read_sock)
                continue

            data = data.strip()
            if not data:
                continue

            key = clients.index(read_sock)

            iam_usernames = re.findall(r"^iam:(.+)$", data)
            if iam_usernames:
                auth_clients[key] = iam_usernames[0]
                data = "New user (%s) input into chat. Hello (%s)!!!" % (iam_usernames[0], iam_usernames[0])
                print data
            else:
                if key in auth_clients:
                    username = auth_clients[key]
                else:
                    username = "Anon%s" % key

                data = "[%s]: %s" % (username, data)


            for write_sock in clients:
                if write_sock != sock:
                    write_sock.send(data + "\n")

    sock.close()

if __name__ == "__main__":
    run_server('', 9051)