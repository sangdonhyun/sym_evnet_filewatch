'''
Created on 2012. 10. 12.

@author: Administrator
'''
'''
Created on 2012. 9. 27.

@author: Administrator
'''
import sys
import os
import datetime
import time
import ConfigParser
from ftplib import FTP
import re
import logging
import glob
import logging.handlers
import base64
import hashlib
import paramiko



class Decode():
    
    def _en(self,_in) : return base64.b64encode(_in) 
    
    def _de(self,_in) : return base64.b64decode(_in)
    
    def fenc(self,str):
        e0  = self._en(str)
        e1  = self._en(e0)
        m   = hashlib.md5(e0).hexdigest()
        e1 = e1.replace('=','@')
        e = e1 + '@' + m
        return e
    
    def fdec(self,e):
        r = e.rfind('@')
        if r == -1:
            pass
        d1  = e[:r]
        d1  = d1.replace('@','=')
        d0  = self._de( d1 );
        d   = self._de( d0 );
        return d

    def decBit(self,fileName):
        with open(fileName) as f:
            tmp = f.read()
        if re.search('###\*\*\*',tmp):
            return True
        else:
            return False
    
    def fileDec(self,fileName):
        if self.decBit(fileName):
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName,'w') as f:
            f.write(self.fdec(str))
        return self.decBit(fileName)
    
    def fileDecReText(self,fileName):
        if self.decBit(fileName):
            with open(fileName) as f:
                reList = f.read()
            
        else:
            with open(fileName) as f:
                str = f.read()
            reList = self.fdec(str)
        
        return reList
        
    
    def fileEncDec(self,fileName):
        if self.decBit(fileName)==False:
            return None
        with open(fileName) as f:
            str = f.read()
        with open(fileName,'w') as f:
            f.write(self.fenc(str))
        return self.decBit(fileName)
    
    
        
class Common():
    def __init__(self):
        
        self.server,self.user,self.passwd=None,None,None
        self.cfg = self.getCfg()
        self.env = os.environ


        
    def hitachiConfig(self):
        if os.path.isdir(self.logDir) == False:
            os.mkdir(self.logDir) 
        if os.path.isdir(self.confDir) == False:
            os.mkdir(self.confDir)
        if os.path.isdir(self.dataDir) == False:
            os.mkdir(self.dataDir)
    
    def getCfg(self):
        
        cfgFile = os.path.join('config','config.cfg')
        if os.path.isfile(cfgFile) == False:
            self.sysOut('cfg file problem')
        config = ConfigParser.RawConfigParser()
        config.read(cfgFile)
        
        self.server=config.get('server','ip')
        self.user=config.get('server','user')
        self.passwd=Decode().fdec(config.get('server','passwd'))
        return config
    
    
    
    def flog(self):
        if not os.path.isdir('log'):
            os.mkdir('log')
        LOG_FILENAME=os.path.join('log','sym_evnetlog.log')
        
#        if None == self.logger:
#            self.logger=logging.getLogger('fleta')
#            self.logger.setLevel(logging.DEBUG)
#            now = datetime.datetime.now()
#            handler=logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=3)
#            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#            handler.setFormatter(formatter)
#            self.logger.addHandler(handler)
#        return self.logger
        logger=logging.getLogger('sym_evnetlog')
        if not len(logger.handlers):
            logger.setLevel(logging.DEBUG)
            now = datetime.datetime.now()
            handler=logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=3)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    
    def fletaPutFtp(self,filename, chdir='Hitachi.disk'):
        
        print self.server
        print self.user
        print self.passwd
        print filename
        
        ftp = FTP(self.server)
        ftp.login(self.user, self.passwd,2)
        ftp.cwd(chdir)
        remote_file = os.path.basename(filename)
        print remote_file
        print remote_file in ftp.nlst()
        rc = ftp.storlines('STOR '+remote_file, open(filename, 'r'))
        print remote_file in ftp.nlst()
        self.sysOut('FTP :'+rc)
        
        if re.search('complete',rc):
            rcBit = True
        else:
            self.sysOut('FTP TRAN FAIL :%s'%rc)
            rcBit = False
        ftp.close()
        sys.stdout.write('FTP SUCC')

        return rc
    
    def sysOut(self,msg):
        logger = self.flog()
        logger.info(msg)
        sys.stdout.write(msg+'\n')
    
    
    def getNow(self,format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format)

    def getHeadMsg(self,title='FLETA BATCH LAOD'):
        now = self.getNow()
        msg = '\n'
        msg += '#'*79+'\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#### '+('TITLE     : %s'%title).ljust(71)+'###\n'
        msg += '#### '+('DATA TIME : %s'%now).ljust(71)+'###\n'
        msg += '#### '+' '*71+'###\n'
        msg += '#'*79+'\n'
        return msg
    
    def getEndMsg(self):
        now = self.getNow()
        msg = '\n'
        msg += '#'*79+'\n'
        msg += '####  '+('END  -  DATA TIME : %s'%now).ljust(70)+'###\n'
        msg += '#'*79+'\n'
        return msg
    
    
def decodeTest():
    li=glob.glob('D:\\Fleta\\data\\diskinfo.SCH\\*.tmp')
#    for i in li:
#        decBit = Decode().decBit(i)
#        print i,decBit
#            
#        
#        if decBit :
#            print 'encoding...'
#            print Decode().fileEnc(i)
#        else:
#            print 'decoding...'
#            print Decode().fileDec(i)
    for i in li:
        print Decode().fileDecReText(i)

def logTest():
    common = Common()
    logger=common.flog()
    logger.info('log test')
    
    

if __name__=='__main__':
#    logTest()
#    fname=os.path.join('data','fs_ibk-test05.tmp')
#    print os.path.isfile(fname)
#    print Common().fletaPutFtp(fname,'diskinfo.SCH')
    logTest()


    
    
    
