#!/usr/bin/python
# -*- coding: utf-8 -*-

# Test on python 3.6

import struct,socket,sys
import hashlib
import threading,random
import time
from base64 import b64encode, b64decode

global GClientList
GClientList = {}

#python3k 版本recv返回字节数组
def decode(data):
    if not len(data):
        return False
    length = data[1] & 127
    if length == 126:
        mask = data[4:8]
        raw = data[8:]
    elif length == 127:
        mask = data[10:14]
        raw = data[14:]
    else:
        mask = data[2:6]
        raw = data[6:]
    ret = ''
    for cnt, d in enumerate(raw):
        ret += chr(d ^ mask[cnt%4])
    return ret

def encode(data):  
    data=str.encode(data)
    head = b'\x81'

    if len(data) < 126:
        head += struct.pack('B', len(data))
    elif len(data) <= 0xFFFF:
        head += struct.pack('!BH', 126, len(data))
    else:
        head += struct.pack('!BQ', 127, len(data))
    return head+data

class WebSocket(threading.Thread):

    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self,conn,index,name,remote, path="/"):
        threading.Thread.__init__(self)
        self.conn = conn
        self.index = index
        self.name = name
        self.remote = remote
        self.path = path
        self.buffer = ""     
    def run(self):
        print('Socket%s Start!' % self.index)
        headers = {}
        self.handshaken = False

        while True:
            if self.handshaken == False:
                print ('Socket%s Start Handshaken with %s!' % (self.index,self.remote))
                self.buffer += bytes.decode(self.conn.recv(1024))

                if self.buffer.find('\r\n\r\n') != -1:
                    header, data = self.buffer.split('\r\n\r\n', 1)
                    for line in header.split("\r\n")[1:]:
                        key, value = line.split(": ", 1)
                        headers[key] = value

                    headers["Location"] = ("ws://%s%s" %(headers["Host"], self.path))
                    key = headers['Sec-WebSocket-Key']
                    token = b64encode(hashlib.sha1(str.encode(str(key + self.GUID))).digest())

                    handshake="HTTP/1.1 101 Switching Protocols\r\n"\
                        "Upgrade: websocket\r\n"\
                        "Connection: Upgrade\r\n"\
                        "Sec-WebSocket-Accept: "+bytes.decode(token)+"\r\n"\
                        "WebSocket-Origin: "+str(headers["Origin"])+"\r\n"\
                        "WebSocket-Location: "+str(headers["Location"])+"\r\n\r\n"
                        
                    self.conn.send(str.encode(str(handshake)))
                    self.handshaken = True  
                    print ('Socket%s Handshaken with %s success!' %(self.index, self.remote))  
                    sendMessage('Welcome, ' + self.name + ' !')  

            else:
                msg=decode(self.conn.recv(1024))    
                if msg=='quit':
                    print ('Socket%s Logout!' % (self.index))
                    nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
                    sendMessage('%s %s say: %s' % (nowTime, self.remote, self.name+' Logout'))                      
                    deleteconnection(str(self.index))
                    self.conn.close()
                    break
                else:
                    print ('Socket %s Got msg:%s from %s!' % (self.index, msg, self.remote))
                    nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
                    sendMessage('%s %s say: %s' % (nowTime, self.remote, msg))       
                
            self.buffer = ""


class WebSocketServer(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.socket = None
        self.ip = ip
        self.port = port
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip ,self.port))
        self.socket.listen(50)

        print( 'WebSocketServer Start!')
        sid = 0
        while True:
            connection, address = self.socket.accept()
            username = address[0]  
            print("new client conn: "+ username )
            newSocket = WebSocket(connection,sid, username, address)
            newSocket.start()
            GClientList['conn_'+str(sid)] = connection
            sid = sid + 1

def sendMessage(message):
    for connection in GClientList.values():
        connection.send(encode(message))
 
def deleteconnection(item):
    del GClientList['conn_'+item]


## 启动服务
def StartServer(port = 8012):
    localip = getLocalIP()
    print(localip)
    server = WebSocketServer(localip, port)
    server.start()
    
def getLocalIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


if __name__ == "__main__":
    import json
    import time

    StartServer()
    data = { 'msg_type' : 99981 , 'timems' : 1, 'code': 'ru1801' ,'realpx' : 98, 'predict' : 100 }
    msg = json.dumps(data)
    
    while(True):
        sendMessage(msg)
        print("sendmsg: %s" % msg)
        time.sleep(3)


    


 

