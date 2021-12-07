# -*- encoding:utf-8*-    
'''
Created on 2013. 2. 11.

@author: Administrator
'''

import sys
import os
import psycopg2
import ConfigParser
import codecs
import locale
import common
import time



class FletaDb():
    def __init__(self):
        self.com = common.Common()
        self.dec = common.Decode()
#         self.logger = self.com.flog()
                
#         self.conn_string = "host='localhost' dbname='fleta' user='fletaAdmin' password='kes2719!'"
        self.conn_string = self.getConnStr()
        self.cfg = self.getCfg()
        self.dfile = os.path.join(self.com.confDir,'dfile.txt')
        self.stime = self.getStime()
        
        self.etime=self.getEtime()
        self.logFileName = self.getLogFile()
        print self.logFileName
        
        



    def getLogFile(self):
        return self.cfg.get('common','logfilename')
            
    
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join(self.com.confDir,'config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getConnStr(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join(self.com.confDir,'config.cfg')
        cfg.read(cfgFile)
        ip = cfg.get('database','ip')
        user = cfg.get('database','user')
        dbname = cfg.get('database','dbname') 
        passwd = cfg.get('database','passwd')
        
        
        if len(passwd)>20:
            try:
                passwd= self.dec.fdec(passwd)
            except:
                pass
        
        return "host='%s' dbname='%s' user='%s' password='%s'"%(ip,dbname,user,passwd)
        
    
    def getConnectInfo(self):
        dbinfo = {}
        for info in self.cfg.options('database'):
            val = self.cfg.get('database',info)
            if (info == 'passwd' or info == 'user') and len(val) >20:
                val - self.dec.fdec(val)
            dbinfo[info] = val
        return dbinfo
    
    def getNow(self,format='%Y%m%d %H:%M:%S'):
        return self.com.getNow(format)
    
    
    def getMsg(self,msgInfo):
        msg=''
        
    
    
    def evtInsert(self,insquery):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
            print insquery
            cur.execute(insquery)
            con.commit()
            
#             print "Number of rows updated: %d" % cur.rowcount
               
        
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()

    
    def dbInsert(self,values):
        con = None
        try:
             
            con = psycopg2.connect(self.conn_string)
            cur = con.cursor()
#                         
            insquery = """
            INSERT INTO pm_auto_trap_info("""+','.join(values.keys())+""")
    VALUES %s;

            """%str(tuple(values.values()))
            print insquery
            cur.execute(insquery)
            con.commit()
            
#             print "Number of rows updated: %d" % cur.rowcount
               
        
        except psycopg2.DatabaseError, e:
            
            if con:
                con.rollback()
            
            print 'Error %s' % e    
            sys.exit(1)
            
            
        finally:
            
            if con:
                con.close()
    
    def getQuery(self):
        queryfile = os.path.join(self.com.confDir,'exQuery.txt')
        
        with open(queryfile) as f:
            tmp = f.read()

        tmp = tmp.replace('<STARTTIME>',self.stime)
        tmp = tmp.replace('<ENDTIME>',self.etime)
        
        print tmp
        return tmp
    def insQuery(self):
        
        query = self.getQuery()
        print query
        self.evtInsert(query)


    def eventList(self):
        query_string = self.getQuery()
        db=psycopg2.connect(self.conn_string)
        cursor = db.cursor()
        
        
        cursor.execute(query_string)
        rows = cursor.fetchall()
        
        if rows == None:
            self.com.sysOut('Empty result set from query')

        cursor.close()
        db.close()
        return rows

    def getStime(self):
        stime = ''
        
        if os.path.isfile(self.dfile):
            with open(self.dfile) as f:
                stime = f.read()
        else:
            stime = self.com.getNow('%Y%m%d 00:00:00')

        if stime == '':
            stime = self.com.getNow('%Y%m%d 00:00:00')
        return stime

    def getEtime(self):
        return self.com.getNow('%Y%m%d %H:%M:%S')
    
            
                
    def dwrite(self,etime):
        with open(self.dfile,'w') as f:
            f.write(etime)
    def runQuery(self):


        self.stime = self.getStime()
        self.etime = self.getEtime()
        
        print 'stime :',self.stime
        print 'etime :',self.etime
        self.dwrite(self.etime)
        
        



        evList=self.eventList()
        print 'EVENT COUNT :',len(evList)
        for ev in evList:
            datetime=ev[4].strip()
            serial = ev[1].strip()
            level=ev[6].strip()
            desc =ev[5].strip()
            msg= '[%s] [%s] %s %s '%(datetime,level,serial,desc)
            self.fwrite(msg)
            print msg

    def fwrite(self,msg):
#         with open(self.logFileName,'a') as f:
#             f.write(msg)
#             f.write('\n')
        
        with codecs.open(self.logFileName,encoding='ms949', mode='a',errors='strict') as f:
            f.write(msg)
            f.write('\n')
                  

    def main(self):
        cnt=0
        try:delay=int(self.cfg.get('common','delaysec'))
        except:delay=30
        while True:
            try:
                self.stime = self.getStime()
                self.etime = self.getEtime()
                
                print 'stime :',self.stime
                print 'etime :',self.etime
                self.dwrite(self.etime)

                evList=self.eventList()
                print 'EVENT COUNT :',len(evList)
                for ev in evList:
                    datetime=ev[4].strip()
                    serial = ev[1].strip()
                    level=ev[6].strip()
                    desc =ev[5].strip()
                    msg= '[%s] [%s] %s %s '%(datetime,level,serial,desc)
#                     msg=msg.decode('utf-8').encode('ms949')
#                     msg=msg.decode('ms949').encode('utf-8')
                    self.fwrite(msg)
                    print msg
            except:
                pass
            time.sleep(delay)

    def mainB(self):
        cnt=0
       
        print self.com.getHeadMsg('FELTA EVENT DB WATCH')
        self.stime = self.getStime()
        self.etime = self.getEtime()
#         self.stime = '20121219 17:54:49'
        print 'stime :',self.stime
        
        print 'etime :',self.etime
        self.dwrite(self.etime)

        evList=self.eventList()
        print 'EVENT COUNT :',len(evList)
        for ev in evList:
            datetime=ev[4].strip()
            serial = ev[1].strip()
            level=ev[6].strip()
            desc =ev[5].strip()
            msg= '[%s] [%s] %s %s '%(datetime,level,serial,desc)
#             print type(msg).__name__
#             print type(msg.decode('utf-8')).__name__
#             print repr(msg)
            msg=msg.decode('utf-8')
            msg=msg.decode('utf-8').encode('ms949')
            self.fwrite(msg)
            print repr(msg)
            print msg
   
        
        print self.com.getEndMsg()

    

if __name__ == '__main__':
    
    FletaDb().main()
#     FletaDb().mainB()
    
    
        
