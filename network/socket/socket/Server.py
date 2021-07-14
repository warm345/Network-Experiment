import socket
import time
import sys
import threading
import queue
import hashlib
import struct
import json
import os
import os.path
from concurrent.futures import ThreadPoolExecutor

IP = '127.0.0.1' #服务器IP
PORT  = 6789    #服务器端口 
PORT1 = 5678    #语音通话时的端口

msgs = queue.Queue() #消息队列
users = [] #存放用户列表以及用户状态
lock = threading.Lock() #避免多个线程保卫同一块数据的时候，产生错误，所以加锁来防止这种问题
# lock1 = threading.Lock()
Thread_pool = ThreadPoolExecutor(max_workers=1000)

#统计在线人员
def onlines(): 
    online = []
    online.append(len(users))
    for i in range(len(users)):
        online.append(users[i][0])
    return online

class ThreadServer1(threading.Thread):
    global users,que,lock

    def __init__(self):
        threading.Thread.__init__(self)
        self.ServerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        os.chdir(sys.path[0])

    def receive(self,conn,addr):
        # 接收客户端发来的用户名并放到用户列表里
        userName = conn.recv(1024)
        userName = userName.decode()
        count = 0
        temp = userName
        # 一旦发生用户名相同的情况，在其后面加上数字
        for i in range(len(users)):
            if users[i][0] == userName:
                count = count + 1
                userName = temp + '(' + str(count) + ')'
        users.append((userName,conn))
        OnlineUsers = {'depcode':2,'msg':onlines()}
        self.msgPut(addr,OnlineUsers)
        #不断接受客户端发来的消息并放入消息队列
        try:
            while True:
                head = conn.recv(4)
                msgsize = struct.unpack("i",head)[0]
                print(msgsize)
                msg = conn.recv(msgsize)
                msg = msg.decode()
                msg = json.loads(msg)
                #文件处理
                if msg['depcode']==3:
                    filename,filesize = msg['msg'].split('~')
                    # 文件大小
                    filesize = int(filesize)
                    temp2 = {'depcode':4,'msg':filename}
                    print(filename,';',filesize)
                    temp2 = json.dumps(temp2)
                    msgsize = struct.pack("i",len(temp2))
                    conn.send(msgsize)
                    conn.send(temp2.encode())
                    print(temp2)
                    f = open(filename, "wb")
                    received_size = 0

                    # 多次传输，防止沾包
                    while received_size < filesize:
                        size = 0 
                        #1024为包的大小进行传输
                        if filesize - received_size > 1024:
                            size = 1024
                        else:  # 最后一次接收完毕
                            size = filesize - received_size
                        data = conn.recv(size)
                        data_len = len(data)
                        received_size += data_len
                        print("已接收：", int(received_size/filesize*100), "%")
                        f.write(data)
                    f.close()
                    temp = {'depcode':5,'msg':userName+'~'+filename}
                    print(temp)
                    self.msgPut(addr,temp)
                elif msg['depcode']==1:
                    msg['msg'] = userName + ':' + msg['msg']
                    self.msgPut(addr,msg)
                # elif msg['depcode']==6:
                #     ms = userName + ':' + msg['msg']
                #     temp = {'depcode':7,'msg':userName+'~'+ms}
                #     self.msgPut(addr,msg)
                elif msg['depcode']==4:
                    filename = msg['msg']
                    
                    if os.path.isfile(filename):
                        print(msg)
                        f = open(filename, 'rb') 
                        size = os.stat(filename).st_size
                        size = str(size)
                        print(filename,';',size)
                        temp3 = {'depcode':3,'msg':filename + '~' + size}
                        temp3 = json.dumps(temp3)
                        msgsize2 = struct.pack("i",len(temp3))
                        conn.send(msgsize2)
                        conn.send(temp3.encode())
                        file_content = f.read()
                        conn.send(file_content)
                    print('ok')
            conn.close()
        #如果用户断开连接，将用户从用户池删除
        except:
            i = 0
            for name in users:
                if name[0] == userName:
                    users.pop(i)
                    break
                i = i + 1
            USERS = {'depcode':2,'msg':onlines()}
            self.msgPut(addr,USERS)
            conn.close()
    #加入消息队列函数，防止访问冲突
    def msgPut(self,addr,data):
        lock.acquire()
        try:
            msgs.put((addr,data))
        finally:
            lock.release()
    #从消息队列中取出消息，防止冲突
    def msgGet(self):
        lock.acquire()
        try:
            data = msgs.get()
        finally:
            lock.release()
        return data 

    #发送消息队列中消息
    def sendData(self):
        while True:
            #如果不空进行下述操作
            if not msgs.empty():
                #获取消息队列中的数据
                data = self.msgGet()
                temp = data[1]
                #数据为消息
                if temp['depcode']==1: 
                    for i in range(len(users)):
                        temp['msg'] = ' ' + temp['msg']
                        temp2 = json.dumps(temp)
                        msgsize = struct.pack("i",len(temp2))
                        try:
                            users[i][1].send(msgsize)
                            users[i][1].send(temp2.encode())
                        except:
                            pass
                        print(temp['msg'])
                        print('\n')
                # 数据为用户列表
                elif temp['depcode']==2: 
                    userPool = json.dumps(temp)
                    msgsize = struct.pack("i",len(userPool))
                    for i in range(len(users)):
                        try:
                            users[i][1].send(msgsize)
                            users[i][1].send(userPool.encode())
                        except:
                            pass
                #文件
                elif temp['depcode']==5:
                    userName = temp['msg'].split('~')[0]
                    temp2 = json.dumps(temp)
                    msgsize = struct.pack("i",len(temp2))
                    for i in range(len(users)):
                        try:
                            if users[i][0] != userName:
                                users[i][1].send(msgsize)
                                users[i][1].send(temp2.encode())
                                print(users[i][0])
                        except:
                            pass
    def run(self):
        self.ServerSocket.bind((IP,PORT))
        self.ServerSocket.listen(5)
        threadSend = threading.Thread(target=self.sendData)
        threadSend.start()
        while True:
            conn,addr = self.ServerSocket.accept()
            threadRecv = threading.Thread(target=self.receive,args=(conn,addr))
            threadRecv.start()
            # threadRecv = Thread_pool.submit(self.receive,conn,addr)
        self.ServerSocket.close()

class ThreadServer2(threading.Thread):

    def __init__(self):
        self.s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)
        self.connections = []

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s1 and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self, c, addr1):
        while 1:
            try:
                data = c.recv(1024)
                print(data)
                self.broadcast(c, data)
 
            except socket.error:
                c.close()
    def run(self):
        
        self.s1.bind((IP,PORT1))
        self.s1.listen(100)
        while True:
            c, addr1 = self.s1.accept()
            self.connections.append(c)
            threading.Thread(target=self.handle_client, args=(c, addr1)).start()
        self.s1.close()

if __name__ == '__main__':
    server1 = ThreadServer1()
    server2 = ThreadServer2()
server1.start()
server2.start()


        
