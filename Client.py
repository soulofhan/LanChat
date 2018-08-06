import socket,select,sys
from threading import currentThread, Thread
import threading
 
HOST='127.0.0.1'        #服务器地址
PORT=5963               #监听端口
BUFSIZE=1024            #数据长度

addr=(HOST,PORT)
mSocket=socket.socket()       #创建mSocketocket连接
mSocket.connect(addr)

inputs = [mSocket, ]
outputs = []
    
def limSocket(mSocket):
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        if mSocket in readable:
            try:
                data = mSocket.recv(BUFSIZE).decode()
                if not data:
                    continue
                    
                if data == 'disconnect':
                    break
                else :
                    print (data)        #打印输出接收自服务器的数据
                
            except Exception as exceptional:
                print ('stocket is error %s' %exceptional)
                break;
    mSocket.close()
    print('再按一次回车键退出')
    
def talk(mSocket):
    while True:
        info=input('')
        try:
            mSocket.send(info.encode())
            if not info:
                print('不能发送空消息,请重新输入')
                continue
            
        except Exception as exceptional:
            print ('can\'t input: %s' % exceptional)
            break
                
    
def main():
    limThread=threading.Thread(target=limSocket,args=(mSocket,))        #消息接收线程
    limThread.start()
    talkThread=threading.Thread(target=talk,args=(mSocket,))            #消息发送线程
    talkThread.start()
    
if __name__=='__main__':
    main()