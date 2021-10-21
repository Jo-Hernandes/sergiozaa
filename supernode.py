# %% 
import socket
import threading
import sys

class MyException(Exception):
    pass

class SuperNode():
    
    def __init__(self, HOST='localhost', PORT=7734):
        self.HOST = HOST
        self.PORT = PORT
        
        self.peers = []
        self.lock = threading.Lock()

    # start listenning
    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.HOST, self.PORT))
            self.s.listen(5)
            print("Supernode up on {0} is listening on port {1}".format(*[self.HOST, self.PORT]))

            while True:
                socs, addr = self.s.accept()
                print('%s:%s connected' % (addr[0], addr[1]))
                thread = threading.Thread(
                    target=self.handle_request, 
                    args=(socs, addr))
                thread.start()
                
        except KeyboardInterrupt:
            print('\nShutting down the server..\nGood Bye!')
            sys.exit(0)

    def handle_request(self, socs, address):
        while True:
            req = socs.recv(1024).decode()
            print(address)
            print('Recieve request:\n%s' % req)
            lines = req.splitlines()
            action = lines[0]
            action_dict = {
                'list': self.list,
                'find': self.find,
                'keep-alive': self.keep_alive
                }
            action_dict.setdefault(action, self.invalid_action)(socs)

    def list(self, socs):
        print("executando list")
        socs.sendall(str.encode("resposta do list"))
    
    def find(self, socs):
        socs.sendall(str.encode("resposta do list"))

    def keep_alive(self, socs):
        print("client is alive!")
        
    def invalid_action(self):
        raise MyException('\nAção invalida.')

if __name__ == '__main__':
    SuperNode().start()