import socket
import time
from _thread import *
import pickle
from random import randint

from game_objects import GameInfo

class Server(object):
    def __init__(self, game):
        self.game = game
        host_name = socket.gethostname()
        # self.ip = socket.gethostbyname(host_name)
        # self.ip = '37.76.5.96'
        self.ip = socket.gethostname()
        print(f'host ip: {self.ip}')
        # self.port = randint(9001, 9999)
        self.port = 50001
        self.s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.user_count = 1
        self.clients = []
        try:
            self.s.bind((self.ip, self.port))
            addrinfo = socket.getaddrinfo(self.ip, self.port, family=socket.AF_INET6, proto=socket.SOCK_DGRAM)
        except socket.error as e:
            str(e)
        print(f"addrinfo: {addrinfo}")
        start_new_thread(self.server_list_connection, ())
        # start_new_thread(self.server_loop, ())

    def server_list_connection(self):
        server_list = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_list.connect(("91.227.139.6", 55555))
        msg = 'server'
        data = [self.ip, self.port]
        print(f'data: {data}')
        server_list.send(pickle.dumps(msg))
        answer = pickle.loads(server_list.recv(2048 * 2))
        if answer == 'welcome':
            server_list.send(pickle.dumps(data))
        while not self.game.gameinfo.playing:
            pass
        server_list.close()

    def server_loop(self):
        self.user_count = self.game.gameinfo.bot_num + 1
        while True:
            message, addr = self.s.recvfrom(2048 * 4)  # UDP
            print(f"{message}")
            if addr in self.clients:
                user_number = self.game.gameinfo.bot_num + 1 + self.clients.index(addr)
                try:
                    self.game.gameinfo.update(user_number, self.game.players)
                    self.s.sendto(pickle.dumps(self.game.gameinfo), addr)
                except Exception as e:
                    print(f"Class: Server Function: server_loop 0 Error-message: {e}")
                try:
                    client_move = pickle.loads(message)
                    if client_move[2]:
                        self.game.players[user_number].sprite.ready = True
                    self.game.players[user_number].sprite.client_move[0] = client_move[0]
                    self.game.players[user_number].sprite.client_move[1] = client_move[1]
                except Exception as e:
                    print(f"Class: Server Function: server_loop 1 Error-message: {e}")
                    break
            else:
                if self.user_count < self.game.gameinfo.players_num:
                    try:
                        print(f"Connected address: {addr}")
                        self.clients.append(addr)
                        username = message.decode()
                        self.game.players[self.user_count].sprite.name = f"{username}"
                        self.game.gameinfo.update(self.user_count, self.game.players)
                        # print(self.game.gameinfo)
                        self.s.sendto(pickle.dumps(self.game.gameinfo), addr)
                        self.user_count += 1
                    except Exception as e:
                        print(f"Class: Server Function: server_loop 2 Error-message: {e}")
                        break


class Client(object):
    def __init__(self, game, server):
        self.game = game
        # self.ip = socket.gethostname()
        # self.port = randint(8000, 9000)
        self.ip = '0.0.0.0'
        self.port = 50002
        # self.server = (server[0], server[1])
        self.server = (('fd02:b67e:88d3:9100:ddf9:a4c6:184:631d', 50001))
        self.s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        try:
            self.s.bind((self.ip, self.port))
        except socket.error as e:
            str(e)
        self.handshake(self.game.user.name)
        # start_new_thread(self.data_exchange, ())


    def data_exchange(self):

        while True:
            try:
                self.s.sendto(pickle.dumps(self.game.client_controls), self.server)
            except Exception as e:
                print(f"Class: Client Function: data_exchange - send Error-message: {e}")
                break
            try:
                message, _ = self.s.recvfrom(2048 * 4)
                self.game.gameinfo = pickle.loads(message)
                self.game.unload_gameinfo()
                # print(self.game.gameinfo)
            except Exception as e:
                print(f"Class: Client Function: data_exchange - receive Error-message: {e}")
                break

    def handshake(self, data):
        try:
            print('1')
            print(f"server: {self.server}")
            print(f"client: {self.ip}, {self.port}")
            self.s.sendto(str.encode(data), self.server)
            print('2')
            message, _ = self.s.recvfrom(2048 * 4)
            print('3')
            self.game.gameinfo = pickle.loads(message)
            print('4')
            self.game.unload_gameinfo()
            print('5')
            print(self.game.gameinfo)
            # print(f"handshake {message}")
        except socket.error as e:
            print(e)
