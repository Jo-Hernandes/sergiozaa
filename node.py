# %%
from argparse import ArgumentParser
import threading
import socket
import sys
import time
import hashlib
import os
from sendfile import send, receive

class MyException(Exception):
    pass

class Node:
    
    
    def __init__(self, host, port, super_node_ip, super_node_port, folder="/"):
        self.host = host
        self.port = port
        self.supernode_host = super_node_ip
        self.supernode_port = super_node_port
        self.folder = folder
        
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096 # send 4096 bytes each time step
    
    def start(self):
        self.socket = socket.socket()
        self.socket.bind((self.host, int(self.port)))
        self.socket.listen(5)
        print("[*] Listening as {host}:{port}".format(host=self.host, port=self.port))
        
        print("Connecting to supernode [{host}:{port}]".format(host=self.supernode_host, port=self.supernode_port))
        self.supernode_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.supernode_socket.connect((self.supernode_host, self.supernode_port))
        except Exception:
            print('Supernode is not available.')
            return

        print('Connected!!')
        keep_alive_thread = threading.Thread(target=self.keep_alive, args=(self.supernode_socket,))
        keep_alive_thread.start()
        # start thread to handle requests
        handle_peers_thread = threading.Thread(target=self.handle_request, args=(self.socket,))
        handle_peers_thread.start()
        
        self.interface()

    def handle_request(self, socs):
        while True:
            client_socket, address = socs.accept()
            req = client_socket.recv(1024).decode()
            if req != "":
                print('Recieve request:{req}'.format(req=req))
                lines = req.splitlines()
                action = lines[0]
                action_dict = {
                    'send_file': self.send_file_to_peer,
                    }
                action_dict.setdefault(action, self.invalid_action)(client_socket, address, req)
                
    def interface(self):
        action_dict = {
            '1': self.list,
            '2': self.find,
            '3': self.add_file,
            '4': self.get_file,
            '5': self.exit,
            }
        while True:
            try:
                req = input(
                    '\n1: Listar todos, 2: Buscar, 3: Incluir arquivo, 4: Baixar arquivo, 5: Finalizar\nEscolha sua ação: ')
                action_dict.setdefault(req, self.invalid_action)()
            except MyException as e:
                print(e)
          
    def list(self):
        print("Listar todos...")
        l1 = "list\n"
        l2 = "host:{host}\n".format(host=self.supernode_socket.getsockname()[0])
        l3 = "port:{port}\n".format(port=self.supernode_socket.getsockname()[1])
        msg = l1 + l2 + l3
        self.supernode_socket.sendall(msg.encode())
        received = self.supernode_socket.recv(1024).decode()
        print("received from supernode\n")
        print(received)
    
    def find(self):
        print("Buscar arquivo...")
        filename = input("\nDigite o nome do arquivo:")
        l1 = "find\n"
        l2 = "host:{host}\n".format(host=self.supernode_socket.getsockname()[0])
        l3 = "port:{port}\n".format(port=self.supernode_socket.getsockname()[1])
        l4 = "{filename}".format(filename=filename)
        msg = l1 + l2 + l3 + l4
        self.supernode_socket.sendall(msg.encode())
        received = self.supernode_socket.recv(1024).decode()
        print(received)
        
    def add_file(self):
        print("Incluir arquivo...")
        filename = input("\nDigite o nome do arquivo: ")
        with open(filename, "rb") as file:
            h = hashlib.sha256()
            while True:
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)
            l1 = "add_file\n"
            l2 = "host:{host}\n".format(host=self.host)
            l3 = "port:{port}\n".format(port=self.port)
            l4 = f"{h.hexdigest()}\n"
            l5 = f"{filename}\n"

            msg = l1 + l2 + l3 + l4 + l5
            self.supernode_socket.sendall(msg.encode())
            received = self.supernode_socket.recv(1024).decode()
            print(received)

    def send_file_to_peer(self, socs, address, req):
        print("Enviando arquivo...")
        lines = req.splitlines()
        host = lines[1].split(":")[1]
        port = lines[2].split(":")[1]
        filename = lines[3]
        filesize = os.path.getsize(filename)
        
        s = socket.socket()
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, int(port)))
        print("[+] Connected.")
        s.send(f"{filename}{self.SEPARATOR}{filesize}".encode())

        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(self.BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
        print("[+] DONE!")
        
    
    def get_file(self):
        print("Baixar arquivo...")
        filename = input("\nDigite o nome do arquivo:")
        peer_host = input("\nDigite o host:")
        peer_port = input("\nDigite a porta:")

        l1 = "send_file\n"
        l2 = "host:{host}\n".format(host=peer_host)
        l3 = "port:{port}\n".format(port=peer_port)
        l4 = "{filename}".format(filename=filename)
        msg = l1 + l2 + l3 + l4
        s = socket.socket()
        print(f"[+] Connecting to {peer_host}:{peer_port}")
        s.connect((peer_host, int(peer_port)))
        s.sendall(msg.encode())
        

        
    def keep_alive(self, server: socket.socket):
        while True:
            time.sleep(5)
            l1 = "keep-alive\n"
            l2 = "host:{host}\n".format(host=server.getsockname()[0])
            l3 = "port:{port}\n".format(port=server.getsockname()[1])
            msg = l1 + l2 + l3
            server.sendall(msg.encode())

    def exit(self):
        print('\nShutting Down...')
        sys.exit(0)

    def invalid_action(self, socs, req):
        raise MyException('\nAção invalida.')



if __name__=="__main__":
    parser = ArgumentParser(prog='node', description='peer node', allow_abbrev=False)
    parser.add_argument("--host", action="store", type=str, help="host ip", required=True)
    parser.add_argument("--port",   action="store", type=int, help="host port", required=True)
    parser.add_argument("--supernode_ip", action="store", type=str, help="super host ip", required=True)
    parser.add_argument("--supernode_port",   action="store", type=int, help="super host port", required=True)
    parser.add_argument("--folder", action="store", type=str, help="folder with files", required=True)

    args = parser.parse_args()
    
    node = Node(host=args.host, 
                port=args.port, 
                super_node_ip=args.supernode_ip, 
                super_node_port=args.supernode_port, 
                folder=args.folder)
    
    node.start()