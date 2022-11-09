import socket
from _thread import *
import pickle
import sys

class ServerList(object):
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 8000

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.servers = []

        try:
            self.s.bind((socket.gethostname(), self.port))
        except socket.error as e:
            str(e)

        self.s.listen()
        print("listen")
        try:
            self.accept_users()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()



    def accept_users(self):
        print("accepting users")
        while True:

            conn, addr = self.s.accept()
            print(f"Connected address: {addr}")
            conn_type = pickle.loads(conn.recv(2048*2))
            if conn_type == 'client':
                conn.sendall(pickle.dumps(self.servers))
                conn.close()
                print('client connected')
            elif conn_type == 'server':

                start_new_thread(self.client_thread, (conn, addr))
            conn_type = ''


    def client_thread(self, conn, addr):
        print("new server created")
        msg = 'welcome'
        conn.sendall(pickle.dumps(msg))
        data = pickle.loads(conn.recv(2048 * 2))
        self.servers.append(data)
        print("servers")
        print(self.servers)
        while True:
            try:
                data = pickle.loads(conn.recv(2048 * 2))
            except ConnectionResetError:
                print("Lost connection")
                break

            except Exception as e:
                print(f"Function: server_list_client_thread Error-message: {e}")
                break

        self.servers.remove(data)
        print("server removed")
        print(self.servers)
        conn.close()

serverlist = ServerList()

