import socket
import hashlib

import os
import sys

s = socket.socket()
connectedHosts = []

def generateSocket(local_ip):

    port = 501 + len(connectedHosts)
    print(f"[*] Listening as {local_ip}:{port}")

    s.bind((local_ip,port))
    s.listen(5)

    client_socket, address = s.accept() 
    print (f"connectado a {address}")

    client_socket, address = s.accept() 
    print (f"connectado a {address}")


    
def connetToSuperNode():

    local_ip = input("Insira endereco de IP do host -> ")
    port = input("Insira numero da porta -> ")

    s.connect((local_ip, int(port)))
    print("connectado a " + local_ip + ":" + port)

def verifySHA(file_path):
    h = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()

def main():
    # type = sys.argv[1]
    # if type == "SUPER":
    #     generateSocket(sys.argv[2])

    # connetToSuperNode()

   print(verifySHA('testfile.txt'))


if __name__=="__main__":
    main()