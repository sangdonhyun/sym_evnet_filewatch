'''
Created on 2013. 9. 14.

@author: Administrator
'''
from pysnmp.hlapi import *
import os
import datetime
import time
import ConfigParser
import subprocess


import common




class SymEvent():
    def __init__(self):
        self.com = common.Common()
        
        self.cfg = self.getCfg()
        self.delaySec = self.getDelaySec()
        path=os.environ['PATH']
        os.environ['PATH'] = '.\bin;%s'%path
        self.log=self.com.flog()
        
    def sample(self):
        msg="""
        
Symmetrix ID: 000290100592
Time Zone   : Korea Standard Time

Detection time           Dir    Src  Category     Severity     Error Num
------------------------ ------ ---- ------------ ------------ ----------
Wed Jan 09 06:58:08 2013 DF-16B SP   Environment  Error        0x0070
    Environmental Error: Supplemental Power Supply low input AC Voltage

Wed Jan 09 17:31:35 2013 DF-16C SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:31:37 2013 DF-1A  SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:31:51 2013 DF-16D SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:31:56 2013 DF-16A SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:31:58 2013 DF-16B SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:32:22 2013 DF-1D  SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:32:25 2013 DF-1C  SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Wed Jan 09 17:32:31 2013 DF-1B  SP   Environment  Error        0x006a
    Environmental Error: Power Supply B faulted

Thu Jan 10 18:16:33 2013 FA-7C  Symm Device(063D) Informational 0x000b
    A Symmetrix device resynchronization process has started

Detection time           Dir    Src  Category     Severity     Error Num
------------------------ ------ ---- ------------ ------------ ----------
Thu Jan 10 18:21:44 2013 FA-10C Symm Device(063D) Informational 0x0008
    An M1 mirror of a Symmetrix Device is resynchronizing with the M2 mirror
"""
        return msg    
    def getDelaySec(self):
        
        try:
            
            return int(self.cfg.get('common','delaysec'))
        except:
            return 600
    
    def getCfg(self):
        cfg = ConfigParser.RawConfigParser()
        cfgFile = os.path.join('config','config.cfg')
        cfg.read(cfgFile)
        return cfg
    
    def getEvtMsg(self):
        """
        symevent list -start 09/09/2013:00:00
        
        """
#         dateTime = self.com.getNow('%m/%d/%Y:%H:%M')
        dateTime = self.com.getNow('%m/%d/%Y:00:00')
        cmd = 'symevent list -start %s'%dateTime
        evtMsg=os.popen(cmd).read()
        evtMsg=self.sample()
        return evtMsg
    
    def getEvtMsg10(self):

        """
        symevent list -start 09/09/2013:00:00:00
        
        """
        dateTime = self.get30Min()
        cmd = 'symevent list -start %s'%dateTime
        return cmd
#         evtMsg=os.popen(cmd).read()
#         evtMsg = self.execute(cmd)
#         
#         
#         return evtMsg
    
    
    def execute(self,cmd):
        
        p=subprocess.Popen(cmd.split(),shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        out,err= p.communicate()
        
        if err==None:
            return out
        else:
            return err
    
        
    
    
    def getSymIdList(self):
#         cfgList= commands.getoutput('symcfg')
#         print cfgList
        symList=[]
        cfgList= os.popen("symcfg list | grep Local | awk \'{print $1}\'").read()
        
        symList= cfgList.splitlines()
        
        
        symList=['00000','000290100592']
        
        print symList
        for exno in sorted(set(self.cfg.options('exclude'))):
            print exno
            ex=self.cfg.get('exclude',exno)
            if ex in symList:
                print ex
                symList.remove(ex)
            
        
        print symList
        return symList
    
    def evtGet(self,msg):
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
    
    
    
    def runExe(self):
        try:
            cwd=self.cfg.get('ftp','cwd')
        except:
            cwd = 'event'
        
        hostname= os.popen('hostname').read().strip()
        while True:
            cdate = self.com.getNow('%Y%m%d%H%M00')
            bdate = self.get30Min('%Y%m%d%H%M00')
            fileName = os.path.join(self.com.dataDir,'%s_%s_%s.txt'%(hostname,cdate,bdate))
            with open(fileName,'w') as f:
                print self.com.getHeadMsg('SYM EVENT')
                f.write(self.com.getHeadMsg('SYM EVENT')+'\n')
                f.write('###***date***###\n')
                f.write('%s\n'%cdate)
                f.write('###***starttime***###\n')
                f.write('%s\n'%bdate)
                f.write('###***symevent***###\n')
                cmd = self.getEvtMsg10()
                print cmd
                remsg = self.execute(cmd)
                print remsg
                f.write(remsg+'\n')
                f.write(self.com.getEndMsg())
                print self.com.getEndMsg()
            self.com.fletaPutFtp(fileName,cwd)
            print '\nFILENAME : ',fileName
            os.remove(fileName)
            if not os.path.isfile(fileName):
                print 'FILE REMOVE',fileName
#             print 'deley time :%s'%self.delaySec
            time.sleep(self.delaySec)
    
    
    def getEvtMsgSid(self,sid):
        """
        symevent list -start 09/09/2013:00:00
        
        """
#         dateTime = self.com.getNow('%m/%d/%Y:%H:%M')
        dateTime = self.com.getNow('%m/%d/%Y:00:00')
        cmd = 'symevent list -sid %s -start %s'%(sid,dateTime)
        print cmd
        evtMsg=os.popen(cmd).read()
        #sample
        evtMsg=self.sample()
        
        return evtMsg
    
    
    
                
            
    

    def setLastEvt(self,err,sid):
        print err
        evFile=os.path.join('config','%s_dtime.txt'%sid)
        str=','.join([err['symid'],err['Time'],err['Descript']])
        with open(evFile,'w') as fw:
            fw.write(str)
    def getLastEvt(self,sid):
        err=['','','']
        evFile=os.path.join('config','%s_dtime.txt'%sid)
        if os.path.isfile(evFile):
            with open(evFile) as f:
                lastEvt=f.read()
            
        else:
            return err
        try:
            err=lastEvt.split(',')
            if len(err) == 1:
                err=['','','']
        except:
            err=['','','']
        return err
            
   

   
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
            
    def evtGetMsg(self,msg):
        
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
    
    
    def getSymEvent(self,sid):
        print self.com.getHeadMsg('SYMEVET')
        cdate = self.com.getNow('%Y%m%d%H%M00')
        print 'now    date :',cdate
        
        msg=self.getEvtMsgSid(sid)
        print msg
        errList=self.evtGetMsg(msg)
        preLastEvt=self.getLastEvt(sid)
        print preLastEvt
        preDatetime=preLastEvt[1]

        sendErrList=[]
        for err in errList:
#             print err['symid'],err['Time'],err['Descript']
#             print preDatetime,err['Time'],preDatetime > err['Time'],preDatetime < err['Time']
            
            if preDatetime < err['Time']:
                sendErrList.append(err)
                
        
        lastEvt=errList[-1]
        if preLastEvt==['','','']:
            self.setLastEvt(lastEvt,sid)
        
        print 'tottal err count:',len(sendErrList)
        for err in sendErrList:
            logmsg=str(err)
            self.log.debug(logmsg)
            self.send_snmp(err)
        print self.com.getEndMsg()
        
        socketClient.SocketSender(FILENAME=fileName,DIR=targetDir).main()
    def main(self):
        symList=self.getSymIdList()
        try:
            targetDir=self.cfg.get('server','targetDir')
        except:
            targetDir='event'
            
        for sym in symList:
            print 'sym :',sym
            
            self.getSymEvent(sym)
            
            
if __name__ == '__main__':
#     SymEvent().runExe()
    SymEvent().main()
#     SymEvent().FtpTest()
    