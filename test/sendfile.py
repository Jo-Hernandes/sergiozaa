import socket

import os
import sys

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

def getFile(fileKey):
    return "testfile.txt"

def sendFile(host, port, fileKey):
    filename = getFile(fileKey)
    filesize = os.path.getsize(filename)

    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, int(port)))
    print("[+] Connected.")
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
    s.close()
    print("[+] DONE!")


def receiveFile(host, port, fileKey):
    s = socket.socket()
    s.bind((host, int(port)))
    s.listen(5)
    print(f"[*] Listening as {host}:{port}")
    client_socket, address = s.accept() 
    print(f"[+] {address} is connected.")
    
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)

    
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            f.write(bytes_read)

    client_socket.close()
    s.close()


def connect_socket():
    s = socket.socket()


def main():
    type = sys.argv[1]
    if type == "receive":
        receiveFile(sys.argv[2], sys.argv[3], "")
    else:
        sendFile(sys.argv[2], sys.argv[3], "")


if __name__=="__main__":
    main()