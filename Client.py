import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('127.0.0.1', 5963))
sock.send(b'1')
print(sock.recv(1024).decode())
print(sock.recv(1024).decode())
nickName = input('input your nickname: ')
sock.send(nickName.encode())


def sendThreadFunc():
    while True:
        try:
            myWord = input()
            sock.send(myWord.encode())
            # print(sock.recv(1024).decode())
        except ConnectionAbortedError:
            print('Server closed this connection!')
            break
        except ConnectionResetError:
            print('Server is closed!')
            break


def recvThreadFunc():
    while True:
        try:
            otherWord = sock.recv(1024)
            if otherWord == "disconnect" or not otherWord.strip():
                sock.close()
                break
            else:
                print(otherWord.decode())
        except ConnectionAbortedError:
            print('Server closed this connection!')
            break
        except ConnectionResetError:
            print('Server is closed!')
            break


th1 = threading.Thread(target=sendThreadFunc)
th2 = threading.Thread(target=recvThreadFunc)
threads = [th1, th2]

for t in threads:
    t.setDaemon(True)
    t.start()
t.join()
