'''
Created on 2013. 10. 5.

@author: Administrator
'''

from pysnmp.hlapi import *
import os, time
import ConfigParser
import datetime
import sys
import re
import common
import shutil

class SymFileWatch():
    def __init__(self):
        self.com = common.Common()
#         self.logger = self.com.logger
        self.cfg = self.getCfg()
        self.pathToWatch  = self.getPath()
        self.delaySec = int(self.cfg.get('common','delaysec'))
#         self.db = fletaDbms.FletaDb()
        self.logName = self.getLogName()
    def getPath(self):
        return self.cfg.get('common','path_to_watch')
    
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join(self.com.confDir,'config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def evtGet(self,fileName):

        print 'evt get file name  :',fileName
        with open(fileName) as f:
            msg = f.read()
        print msg
        lines = msg.splitlines()
        errList = []
        for i in range(len(lines)):
            line = lines[i]
            
            if 'Symmetrix ID:' in line:
                symId = line.split(':')[1].strip()
                
            evtbit = False
            try:
                strt = ' '.join(line.split()[:5])
                evtTime = datetime.datetime.strptime(strt, "%a %b %d %H:%M:%S %Y")
                evtbit = True
            except:
                evtbit = False
        
            if evtbit:
                evt = {}
                evt['symid']    = symId
                evt['Time'] = datetime.datetime.strftime(evtTime,'%Y-%m-%d %H:%M:%S')
                dt =  line.split()
               
                evt['Dir']      = dt[5]
                evt['Src']      = dt[6]
                evt['Category'] = ' '.join(dt[7:-2])
                evt['Severity'] = dt[-2]
                evt['ErrorNum'] = str(dt[-1])
                evt['Descript'] = lines[i+1].strip()
                
                errList.append(evt)
        
        return errList
    def send_snmp(self,errDic):
        """
        {'Category': 'Device(00BD4)', 'Src': 'Symm', 'Severity': 'Warning', 'symid': '000292603896', 'Descript': 'Access was attempted to a Not Ready device', 'ErrorNum': '0x003f', 'Time': '2018-06-25 10:15:50', 'Dir': 'FA-8G'}
        """
        cfg=ConfigParser.RawConfigParser()
        cfgFile='config\\config.cfg'
        cfg.read(cfgFile)
        print os.path.isfile(cfgFile)
        try:
            snmp_ip=cfg.get('server','snmp_ip')
        except:
            snmp_ip='localhost'
        
        print snmp_ip
        
        
        """
        -v 1.3.6.1.4.1.6485.901.0 STRING 1234567                            <== serial
        -v 1.3.6.1.4.1.6485.901.1 STRING 2019-02-26 02:02:01             <== event_date
        -v 1.3.6.1.4.1.6485.901.2 STRING 0x1234                              <== event_code
        -v 1.3.6.1.4.1.6485.901.3 STRING Warning                             <== severity
        -v 1.3.6.1.4.1.6485.901.4 STRING This is test message              <== desc
        -v 1.3.6.1.4.1.6485.901.5 STRING EMC                                 <== vendor
        -v 1.3.6.1.4.1.6485.901.6 STRING STG                                  <== device_type
        -v 1.3.6.1.4.1.6485.901.7 STRING realtime ssh                                  <== method
        -v 1.3.6.1.4.1.6485.901.8 STRING etc                                  <== etc
        """
        
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((snmp_ip, 162)),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.6485.901'),
                ).addVarBinds(
                    ('1.3.6.1.4.1.6485.901.0', OctetString(errDic['symid'])),
                    ('1.3.6.1.4.1.6485.901.1', OctetString(errDic['Time'])),
                    ('1.3.6.1.4.1.6485.901.2', OctetString(errDic['ErrorNum'])),
                    ('1.3.6.1.4.1.6485.901.3', OctetString(errDic['Severity'])),
                    ('1.3.6.1.4.1.6485.901.4', OctetString(errDic['Descript'])),
                    ('1.3.6.1.4.1.6485.901.5', OctetString('EMC')),
                    ('1.3.6.1.4.1.6485.901.6', OctetString('STORAGE')),
                    ('1.3.6.1.4.1.6485.901.7', OctetString('symevent')),
                    ('1.3.6.1.4.1.6485.901.8', OctetString(errDic['Category'])),
                    
                )
            )
        )
        if errorIndication:
            print(errorIndication)
        
        
    def symEvent(self,added):
        for filename in added:
            filename = os.path.join(self.pathToWatch,filename)
            print 'file name :',filename
            errList = self.evtGet(filename)
            
            print '#'*50
            print 'tot cnt :',len(errList)
            
            print self.cfg.options('common')
            
            try:
                db_inst=self.cfg.get('common','db_insert')
                
                if db_inst.upper() in ['Y','YES','T','TURE']:
                    db_bit=True
                else:
                    db_bit=False
            except:
                db_bit=True
            
                self.evtDbInsert(errList)
            print errList
            try:
                snmp_str=self.cfg.get('common','snmp_send')
                if snmp_str.upper() in ['Y','YES','T','TURE']:
                    snmp_bit=True
            except:
                snmp_bit=True
            for err in errList:
                if snmp_bit:
                    self.send_snmp(err)
            
#             sys.exit()
            mdir = os.path.split(os.path.split(filename)[0])[0]
#             print mdir
            target = os.path.join(mdir,'event.MV',os.path.basename(filename))
            # print 'src',filename
            # print 'tar',target
             
            
            
#             print os.path.isfile(filename)
#             print os.path.isfile(target)
#             if os.path.isfile(filename):
#                 print'move :',filename
                
            if os.path.exists(filename):
                os.remove(filename)
#             time.sleep(0.5)
#             shutil.move(filename, target)



#             print os.path.isfile(filename)
#             print os.path.isfile(target)
#     def dbInsert(self,errList):
#         checkDate = self.com.getNow('%Y-%m-%d %H:%M:%S')
#         
#         for err in errList:
#             
# 
#             etc = 'Dir : %s, Src : %s'%(err['Dir'],err['Src'])
#             dbvalue ={}
#             dbvalue['check_datetime']            = checkDate
#             dbvalue['event_trap_serial_number']  = err['symid'][-5]
#             dbvalue['event_trap_nick_name']      = ''
#             dbvalue['event_trap_refcode']        = err['ErrorNum']
#             dbvalue['event_trap_parts_id']       = err['Category'] 
#             dbvalue['event_trap_datetime']       = err['Time']
#             dbvalue['event_trap_description']    = err['Descript']
#             dbvalue['event_code_level']          = err['Severity']
#             dbvalue['action_event_datetime']     = ''
#             dbvalue['action_memo']               = ''
#             dbvalue['user_id']                   = ''
#             dbvalue['trap_etc']                  = etc
#             
#             
#             
# #             self.db.dbInsert(dbvalue)
#         return errList
        
    
    def run(self):
#         self.logger.info('PROGRAM START')
        path_to_watch = self.pathToWatch
        print self.com.getHeadMsg('SYM FILE WATCHER')
        print 'PATH : ',path_to_watch

        while 1:
            
            fileList=  os.listdir (path_to_watch)
            print 'File :',len(fileList)
            addList  =[]
            for filename in fileList:
                
                with open(os.path.join(path_to_watch,filename)) as f:
                    tmp = f.read()
                if re.search('####  END  -  DATA TIME :',tmp):
                    addList.append(filename)
                    
            self.symEvent(addList)
            time.sleep(self.delaySec)
            
            
#             
#             print 'delay ',self.delaySec
#             time.sleep (self.delaySec)
#             after = dict ([(f, None) for f in os.listdir (path_to_watch)])
#             added = [f for f in after if not f in before]
#             removed = [f for f in before if not f in after]
#             if added: print "Added: ", ", ".join (added)
#             if removed: print "Removed: ", ", ".join (removed)
#             before = after
#             
#             
#             print 'after :',after
#             print 'added :',added,type(added)
#             print 'removed :',removed
#             
#             self.symEvent(added)
            


    def checkChar(self,errInfo):
        
        for err in errInfo.keys():
            if '\'' in errInfo[err]:
                errInfo[err] = errInfo[err].replace('\'','\"')
        return errInfo
    
    def getLogName(self):
        logName = self.cfg.get('common','logfilename')
        if not os.path.isfile(logName):
#             self.logger.error('LOG ERROR')
#             self.logger.error('CHECK LOG PATH IN config.cfg')
            sys.stdout.write('LOG ERROR')
#             sys.exit(-1)
        return logName
    def fwrite(self,msg,wbit='a'):
        
        with open(self.logName,wbit) as f:
            f.write(msg+'\n')
            
    
    def getMsg(self,evt):
        msg  = '[%s] [%s] %s  %s %s '%(evt['Time'],evt['Severity'],evt['symid'],evt['Category'], evt['Descript'])
        return msg
    

    
                
    def mainB(self):
#         self.logger.info('PROGRAM START')
        path_to_watch = self.pathToWatch
        print self.com.getHeadMsg('SYM FILE WATCHER')
        print 'PATH : ',path_to_watch
#         before = dict ([(f, None) for f in os.listdir (path_to_watch)])
#         print 'before :',before,type(before)
        
        
        fileList=  os.listdir (path_to_watch)
        print 'File :',len(fileList)
        addList  =[]
        for filename in fileList:
            
            with open(os.path.join(path_to_watch,filename)) as f:
                tmp = f.read()
            if re.search('####  END  -  DATA TIME :',tmp):
                addList.append(filename)



        self.symEvent(addList)

        print self.com.getEndMsg()
                    
            

if __name__ =='__main__':
    SymFileWatch().run()
    
            
            