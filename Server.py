from socket import *
import select
import _thread
import threading
 
host='0.0.0.0'      #监听ip，0.0.0.0为监听所有网络
port=5963           #监听端口
addr=(host,port)
     
mSocket=socket(AF_INET, SOCK_STREAM)
inputs = [mSocket, ]
outputs = []
fd_name={}
 
def who_in_room(writable):
    name_list=[]
    for k in writable:
        name_list.append(writable[k])
        
    return name_list

def new_coming(mSocket):     #新用户连接时执行
    client,add=mSocket.accept()
    print ('welcome %s %s' % (client,add))
    wel='''welcome into the talking room .
    please decide your name.....'''
    client.send(wel.encode("utf-8"))
    name = ''
    try:
    
        name=client.recv(1024).decode()
        
    except IOError as nIOError:
    
        print('%s %s leave the room' % (client,add))
        
    if name.strip():
        print('name = %s' % name)
        inputs.append(client)
        fd_name[client]=name
        nameList="Some people in talking room, these are %s \n" % (who_in_room(fd_name))
        client.send(nameList.encode("utf-8"))
        tip = "输入disconnect / 退出 可退出房间"
        client.send(tip.encode("utf-8"))
        print(nameList)
    
    
def server_run():       #启动服务器
 
    print ('runing')
    mSocket.bind(addr)
    mSocket.listen(1)        #最大可阻塞连接数
    
    inputs.append(mSocket)
    
    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for temp in readable:
            if temp is mSocket:
                new_coming(mSocket)
            else:
                disconnect=False
                try:
                    data= temp.recv(1024).decode()      #接收客户端的数据(阻塞)
                    if data == 'disconnect' or data == '退出':
                        data=fd_name[temp]+' leave the room'
                        disconnect=True
                    else:
                        data=fd_name[temp]+' say : '+data
                except Exception as exceptional:
                    print ('recv exceptional %s' % exceptional)
                    data=fd_name[temp]+' leave the room'
                    disconnect=True
                
                if disconnect:
                    print ('disconnect %s' % data)
                    for other in inputs:
                        if other!=mSocket and other!=temp:
                            try:
                                other.send(data.encode("utf-8"))
                            except Exception as exceptional:
                                print ('disconnect exceptional %s' % exceptional)
                                
                        if other == temp:               #返回断开连接消息给客户端
                            try:
                                other.send('disconnect'.encode("utf-8"))
                            except Exception as exceptional:
                                break
                    del fd_name[temp]
                    temp.close()
                    inputs.remove(temp)
                    
                else:
                    print ('客户端',data)
                    
                    for other in inputs:
                        if other!=mSocket and other!=temp:
                            try:
                                other.send(data.encode("utf-8"))
                            except Exception as exceptional:
                                print ('send all %s but %s leave the room' % exceptional %fd_name[other])
                                
    
if __name__=='__main__':
    server_run()