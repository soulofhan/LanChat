import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('0.0.0.0', 5963))

sock.listen(10)
print('Server', socket.gethostbyname('0.0.0.0'), 'listening ...')

myDict = dict()  # 当前在线人员昵称列表
myList = list()  # 当前socket在线客户端列表


# 向除自己外的所有人发送消息
def tellOthers(exceptNum, whatToSay):
    for othersClient in myList:
        if othersClient.fileno() != exceptNum:
            try:
                othersClient.send((whatToSay + '\n').encode())
            except Exception as mException:
                print('22 exception is : %s' % mException)


# 向自己发送消息
def tellMySelf(exceptNum, whatToSay):
    for myClient in myList:
        if myClient.fileno() == exceptNum:
            try:
                myClient.send((whatToSay + '\n').encode())
            except Exception as e:
                print('32 exception is : %s' % e)


# 向所有人发送服务器公告
def notificationAll(bulletin):
    whatToSend = '[proclamation]:[%s]' % bulletin
    for allClient in myList:
        try:
            allClient.send((whatToSend + '\n').encode())
        except Exception as e:
            print('44 exception is : %s' % e)


def isName(nickName):
    nameList = list(myDict.values())
    if nickName not in nameList and nickName.split():
        print('50 传入的值为 %s 列表为 %s' % (nickName, nameList))
        return True  # 不在列表中返回True
    return False


# 向所有人发送当前在线人数
def sendAll():
    online = str(len(myDict))
    onlineSend = '[decide]:[%s]' % online
    for allClient in myList:
        try:
            allClient.send((onlineSend + '\n').encode())
        except Exception as e:
            print('63 exception is : %s' % e)


def subThreadIn(myConnection, connNumber):
    nickname = ''
    disconnect = False
    mContinue = True
    while True:
        try:
            nickname = myConnection.recv(1024).decode()
        except IOError as mIOError:
            print('72 recv exceptional %s' % mIOError)
        if nickname == 'disconnect':
            myConnection.send('disconnect\n'.encode())  # 发送终止链接指令
            mContinue = False
            myConnection.close()
            print('79 close the connection %s' % myConnection)
            break
        else:
            if isName(nickname):
                myDict[connNumber] = nickname  # 将初始化昵称加入至在线人列表
                myList.append(myConnection)  # 将连接加入在线客户端列表
                myConnection.send('[correct]:[success]\n'.encode())  # 发送链接成功
                break
            else:
                myConnection.send('[correct]:[failure]\n'.encode())  # 发送链接失败
                continue

    if mContinue:
        print('81 connection', connNumber, ' has nickname :', nickname)
        # 向其他人发送自己加入房间
        tellOthers(connNumber, '[enter]:[' + myDict[connNumber] + ']')
        # 向自己发送当前在线人员
        tellMySelf(connNumber, '[Tip]:%s' % list(myDict.values()))
        sendAll()
        while True:
            if disconnect:
                tellMySelf(connNumber, 'disconnect')  # 向自己发送断开连接指令
                leave(myConnection, connNumber)  # 告诉其他人我已离开
                sendAll()
                return
            else:
                try:
                    recvedMsg = myConnection.recv(1024).decode()  # 阻塞接收消息
                    if recvedMsg == 'disconnect' or not recvedMsg.strip():  # 如果收到'disconnect' 则将退出位置True
                        disconnect = True
                    else:
                        print('100', myDict[connNumber], ':', recvedMsg)  # 输出接收到的消息
                        tellOthers(connNumber, '[Msg]:[' + myDict[connNumber] + ',' + recvedMsg + ']')

                except (OSError, ConnectionResetError):
                    leave(myConnection, connNumber)  # 客户端直接退出时执行异常连接断开
                    return


# 离开函数
def leave(myConnection, connNumber):
    try:
        myList.remove(myConnection)  # 从在线客户端列表中删除自己
    except ValueError as mValueError:
        print('113 mValueError is : %s' % mValueError)
    print('114', myDict[connNumber], 'exit, ', len(myList), ' person left')
    tellOthers(connNumber, '[Dis]:[' + myDict[connNumber] + ']')  # 告诉其他人自己离开
    myDict.pop(connNumber)  # 从在线人员昵称列表中删除自己
    myConnection.close()  # 关闭连接


def notification():
    while True:
        notificationMsg = input()
        notificationAll(notificationMsg)


# 启动一个系统通知线程
sendThread = threading.Thread(target=notification)
sendThread.start()

# 循环等待客户端接入
while True:
    connection, addr = sock.accept()  # 阻塞接入客户端
    print('122 Accept a new connection', connection, connection.getsockname(), connection.fileno(), addr)
    try:
        # connection.settimeout(5)
        buf = connection.recv(1024).decode()
        if buf == '1':
            connection.send('[wel]:[welcome]\n'.encode())
            connection.send(('[decide]:[' + str(len(myList)) + ']\n').encode())

            # 为当前连接开辟一个新的线程
            myThread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))
            myThread.setDaemon(True)
            myThread.start()

        else:
            connection.send('please go out!'.encode())
            connection.close()
    except Exception as exception:
        print('139 exception is : %s' % exception)
