# %% 
from argparse import ArgumentParser
import socket
import threading
import sys
import struct
import time

class MyException(Exception):
    pass

class SuperNode():
    
    def __init__(self, HOST='localhost', PORT=7736):
        self.HOST = HOST
        self.PORT = PORT

        self.peers = []
        self.files = dict({})
        self.lock = threading.Lock()
        self.mcast_group = '224.10.10.10'
        self.mcast_port = 5016

    # start listenning
    def start(self):
        try:
            # create socket to listen nodes connections
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.HOST, self.PORT))
            self.s.listen(5)

            print("Supernode up on {0} is listening on port {1}".format(*[self.HOST, self.PORT]))
            
            # create socket to listen multicast messages
            self.mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.mcast_sock.bind(('', 10000))
            # Tell the operating system to add the socket to
            # the multicast group on all interfaces.
            self.mcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            group = socket.inet_aton(self.mcast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            # start thread to listen multicast messages
            mcast_thread = threading.Thread(target=self.handle_mcast_message, args=(self.mcast_sock,))
            mcast_thread.start()

            
            while True:
                socs, addr = self.s.accept()
                print('%s:%s connected' % (addr[0], addr[1]))
                # register peer
                self.peers.append({'host': addr[0], 'port': addr[1], 'isAlive': True})
                print(self.peers)
                # start thread to handle requests
                handle_peers_thread = threading.Thread(target=self.handle_request, args=(socs, addr))
                handle_peers_thread.start()

                # # start timer to verify peers alive
                # thread_verify_peers_alive = threading.Thread(target=self.verify_peers_alive)
                # thread_verify_peers_alive.start()

                # # start timer to force peers live probe
                # thread_force_peers_live_probe = threading.Thread(target=self.force_peers_live_probe)
                # thread_force_peers_live_probe.start()
                
        except KeyboardInterrupt:
            print('\nShutting down the server..\nGood Bye!')
            sys.exit(0)

    def handle_mcast_message(self, socs):
        print("waiting for multicast message")
        while True:
            data, address = socs.recvfrom(1024)
            print('received {} bytes from {}'.format(len(data), address))
            print(data)
        
    def handle_request(self, socs, address):
        while True:
            req = socs.recv(1024).decode()
            if req != "":
                # print('Recieve request:{req}'.format(req=req))
                lines = req.splitlines()
                action = lines[0]
                action_dict = {
                    'list': self.list,
                    'find': self.find,
                    'look_up': self.look_up,
                    'add_file': self.add_file,
                    'keep-alive': self.keep_alive
                    }
                action_dict.setdefault(action, self.invalid_action)(socs, req)

    def list(self, socs, req):
        for filename, metadata in self.files.items():
            l1 = "[{filename} ".format(filename=filename)
            l2 = "host:{host} ".format(host=metadata['host'])
            l3 = "port:{port}]\n".format(port=metadata['port'])
            resp = l1 + l2 + l3
            socs.sendall(str.encode(resp))

    def look_up(self, key):
        return ""

    def search_nodes(self, key):
        l1 = "look_up \n"
        l2 = f'{key} \n'
        for server in self.peers:
            server.sendall(str.encode(l1 + l2))
            received = server.recv(1024).decode()
            if received != "":
                return received
        return ""

    def find(self, socs, req):
        lines = req.splitlines()
        filename = lines[3]
        
        if filename in self.files:
            retrieved_item = self.files[filename]
            print("{filename} found in {retrieved_item}".format(filename=filename, retrieved_item=retrieved_item))
            l1 = "[{filename} ".format(filename=filename)
            l2 = "host:{host} ".format(host=retrieved_item['host'])
            l3 = "port:{port}]\n".format(port=retrieved_item['port'])
            resp = l1 + l2 + l3
            socs.sendall(str.encode(resp))
        else:
            # retrieved_item = self.search_nodes(filename)
            # if (retrieved_item == ""):
                socs.sendall(str.encode("item nao encontrado"))
            # else:
            #     socs.sendall(str.encode(retrieved_item))

    def add_file(self, socs, req):
            lines = req.splitlines()
            host = lines[1].split(':')[1]
            port = lines[2].split(':')[1]
            filename = lines[4]
            hash_value = lines[3]
            self.files[filename] = {'host': host, 'port': port, 'hash': hash_value}
            # print("file {filename} added to the list".format(filename=filename))
            socs.sendall(str.encode("file: '{filename}' added.".format(filename=filename)))

    def keep_alive(self, socs, req):
        # print("lived peers {peers}".format(peers=self.peers))
        lines = req.splitlines()
        host = lines[1].split(':')[1]
        port = lines[2].split(':')[1]
        for peer in self.peers:
            if peer['host'] == host:
                # print("{host}:{port} is alive!".format(host=host, port=port))
                peer['isAlive'] = True

    def verify_peers_alive(self):
        print("verifiy peers live {peers}".format(peers=self.peers))
        while True:
            time.sleep(10)
            self.lock.acquire()
            for peer in self.peers:
                if peer['isAlive'] == False:
                    self.peers.remove(peer)
                    print('{}:{} is dead'.format(peer['host'], peer['port']))
            self.lock.release()

    def force_peers_live_probe(self):
        print("force peers live probe {peers}".format(peers=self.peers))
        while True:
            time.sleep(12)
            self.lock.acquire()
            for peer in self.peers:
                peer['isAlive'] = False
                print('{}:{} setted to die'.format(peer['host'], peer['port']))
            self.lock.release()
            
    

    def invalid_action(self):
        raise MyException('Ação invalida.')

if __name__ == '__main__':
    parser = ArgumentParser(prog='node', description='peer node', allow_abbrev=False)
    parser.add_argument("--host", action="store", type=str, help="host ip", required=True)
    parser.add_argument("--port",   action="store", type=int, help="host port", required=True)

    args = parser.parse_args()
    
    supernode = SuperNode(HOST=args.host, PORT=args.port)
    supernode.start()
