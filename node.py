# %%
import argparse
import threading
import socket
import sys
import time

class MyException(Exception):
    pass

class Node:
    
    def __init__(self, super_node_ip, super_node_port, folder="/"):
        self.supernode_host = super_node_ip
        self.supernode_port = super_node_port
        self.folder = folder
    
    def start(self):
        print("Connecting to supernode [{0}:{1}]".format(*[self.supernode_host, self.supernode_port]))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.supernode_host, self.supernode_port))
        except Exception:
            print('Supernode is not available.')
            return

        print('Connected!!')
        keep_alive_proccess = threading.Thread(
            target=self.keep_alive, 
            args=[self.server])
        keep_alive_proccess.start()
        self.register_receiver()
        self.interface()

    def register_receiver(self):
        ## socket para receber dados
        pass
    
    def interface(self):
        action_dict = {
            '1': self.list,
            '2': self.find,
            '5': self.exit,
            }
        while True:
            try:
                req = input(
                    '\n1: Listar todos, 2: Buscar, 5: Finalizar\nEscolha sua ação: ')
                action_dict.setdefault(req, self.invalid_action)()
            except MyException as e:
                print(e)
          
    def list(self):
        print("Listar todos...")
        l1 = "list\n"
        l2 = "host: nodeip\n"
        l3 = "port: 1010\n"
        msg = l1 + l2 + l3
        self.server.sendall(msg.encode())
        received = self.server.recv(1024).decode()
        print("received from supernode {msg}".format(msg=received))
    
    def find(self):
        print("Buscar arquivo...")
        filename = input("\nDigite o nome do arquivo:")
        print(filename)
        l1 = "find\n"
        l2 = "host:nodeip\n"
        l3 = "port:1010\n"
        l4 = "filename:{filename}".format(filename=filename)
        msg = l1 + l2 + l3 + l4
        self.server.sendall(msg.encode())

    def keep_alive(self, server):
        while True:
            time.sleep(100)
            l1 = "keep-alive\n"
            l2 = "host:{host}\n".format(host=server.getsockname()[0])
            l3 = "port:{port}\n".format(port=server.getsockname()[1])
            msg = l1 + l2 + l3
            server.sendall(msg.encode())

    def exit(self):
        print('\nShutting Down...')
        sys.exit(0)

    def invalid_action(self):
        raise MyException('\nAção invalida.')


if __name__=="__main__":
    parser = argparse.ArgumentParser(prog='node', description='peer node', allow_abbrev=False)
    parser.add_argument("--supernode_ip", action="store", type=str, help="super host ip", required=True)
    parser.add_argument("--port",   action="store", type=int, help="super host port", required=True)

    args = parser.parse_args()
    print(args.supernode_ip)
    print(args.port)

    node = Node(super_node_ip=args.supernode_ip, super_node_port=args.port)
    node.start()

# %%
