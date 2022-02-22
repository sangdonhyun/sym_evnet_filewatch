'''
Created on 2014. 4. 16.

@author: Administrator
'''
import threading, time
import socket
import os
import common
import ast
import glob
import ConfigParser
import random


class SocketSender():
    def __init__(self, **kwargs):
        self.filieName = kwargs['FILENAME']
        self.dir = kwargs['DIR']
        try:
            self.endCheck = kwargs['ENDCHECK']
        except:
            self.endCheck = 'False'
        self.com = common.Common()
        self.dec = common.Decode()
        self.cfg = self.getInfo()

    def getInfo(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config', 'config.cfg')
        cfg.read(cfgFile)
        self.HOST = cfg.get('server', 'ip')
        self.PORT = cfg.get('server', 'port')
        return cfg


    def getReTryCnt(self):
        try:
            cnt = int(self.cfg.get('fleta_agent', 'sock_retry_cnt'))
        except:
            cnt = 5
        return cnt

    def send(self):


#         HOST, PORT = "1.217.179.141", 54001
        HOST = self.HOST
        try:
            PORT = int(self.PORT)
        except:
            PORT = 54001

        fname = self.filieName

        if os.path.isfile(fname) is False:
            s_msg = '%s File Not Found' % (fname)
            self.com.flog().error(s_msg)
            return False

#         print  "send file name :",fname
        info = {}
        info['FLETA_PASS'] = 'kes2719!'
        info['FILENAME'] = os.path.basename(fname)
        info['DIR'] = self.dir
        info['FILESIZE'] = os.path.getsize(fname)
        info['ENDCHECK'] = self.endCheck

#         print info
        dec = common.Decode()

        data = dec.fenc(str(info))
        # print data

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sBit = False

        try:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            sock.sendall(data + "\n")

            # Receive data from the server and shut down
            received = sock.recv(1024)
            print received
            if received == 'READY':
                with open(fname) as f:
                    data = f.read()
                sock.sendall(data)
            sBit = True
        except socket.error as e:
            sBit = False
            print e
            self.com.flog().error(str(e))
        finally:
            sock.close()

        return sBit

    def main(self):
        reCnt = self.getReTryCnt()
        cnt = 0
        s_msg = ''
        while 1:
            sBit = self.send()
            if sBit :
                s_msg = "FILE TRANSFER SUCC BY SOCKET"
                print s_msg
                self.com.flog().info(s_msg)
                break
            else:
                s_msg = 'FLETA SERVER : %s , PORT : %s SEND FILE ERROR RETRY (%d/%d) ' % (self.HOST, self.PORT, cnt + 1, reCnt)
                print s_msg
                self.com.flog().error(s_msg)
            cnt += 1
            if reCnt == cnt:
                break

            time.sleep(random.randint(5, 10))

if __name__ == '__main__':
    fileName = os.path.join('data', '10.25.207.182.log')
    SocketSender(FILENAME=fileName, DIR='Xtrim.disk').main()
