# %% 
import socket
import threading
import sys
from kademlia.network import Server
import asyncio


class MyException(Exception):
    pass

class SuperNode():
    
    def __init__(self, HOST='localhost', PORT=7735):
        self.HOST = HOST
        self.PORT = PORT
        
        self.node = Server()
        self.peers = []
        self.lock = threading.Lock()

    async def initHashNode(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.node.listen(8468))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.node.stop()
            loop.close()

    # start listenning
    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.HOST, self.PORT))
            self.s.listen(5)
            asyncio.run(self.initHashNode())

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


    async def search_file(self, key, socs):
        value = await self.node.get(key)
        print(value)
        if (value is None):
            socs.sendall(str.encode("Arquivo nao encontrado"))
        else: 
            socs.sendall(str.encode(value))

    def find(self, socs, req):
        lines = req.splitlines()
        asyncio.run(self.search_file(lines[3], socs))

    def keep_alive(self, socs, req):
        print("client is alive!")

    async def include_file(self, key, value):
        await self.node.set(key, value)

    def add_file(self, socs, req):
        lines = req.splitlines()
        asyncio.run(self.include_file(lines[1], lines[2]+lines[3]+lines[4]))
        
    def invalid_action(self):
        raise MyException('\nAção invalida.')

if __name__ == '__main__':
    SuperNode().start()
# %%
