# %% 
import socket
import threading
import sys

class MyException(Exception):
    pass

class SuperNode():
    
    def __init__(self, HOST='localhost', PORT=7736):
        self.HOST = HOST
        self.PORT = PORT

        self.peers = []
        self.files = dict({})
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
                'look_up': self.look_up,
                'add_file': self.add_file,
                'keep-alive': self.keep_alive
                }
            action_dict.setdefault(action, self.invalid_action)(socs, req)

    def list(self, socs, req):
        try:
            print("executando list")
            socs.sendall(str.encode("resposta do list"))
        except:
            socs.sendall(str.encode("resposta do list"))

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
        key = lines[3]
        if key in self.files:
            retrieved_item = self.files[lines[3]]
            socs.sendall(str.encode(retrieved_item))
        else:
            retrieved_item = self.search_nodes(key)
            if (retrieved_item == ""):
                socs.sendall(str.encode("item nao encontrado"))
            else:
                socs.sendall(str.encode(retrieved_item))


    def keep_alive(self, socs, req):
        print("client is alive!")

    def add_file(self, socs, req):
        lines = req.splitlines()
        self.files[lines[1]] = f'\n{lines[1]} - {lines[2]} - {lines[3]} - {lines[4]}'
        print(self.files[lines[1]])

    def invalid_action(self):
        raise MyException('Ação invalida.')

if __name__ == '__main__':
    SuperNode().start()
# %%

# %%
