from datetime import datetime,timedelta
import time
from HinetPy import Client,win32
import os
from obspy import read

sDate=datetime(2012,2,1)+timedelta(days=0)#days=30+100+30-400)
count=200# how many day

spanDays=1#365*8
client=Client("***","***")#username passwd
filename="event_lst"
client.get_arrivaltime(sDate,spanDays,filename=filename)

eventDir='eventDir/'
eventDir2='event/'

while count>0:
    try:
        cmd="rm -r "+eventDir+"/D*"
        os.system(cmd)
        count=count-1
        sDate=sDate+timedelta(days=1)
        client.get_arrivaltime(sDate,spanDays,filename=filename)
        ### set requirement
        client.get_event_waveform(sDate.strftime("%Y-%m-%d %H:%M:%S"),\
            (sDate+timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),minmagnitude=-1, maxmagnitude=9.9,\
            include_unknown_mag=True,minlatitude=30, maxlatitude=50, minlongitude=125,\
            maxlongitude=150)
        cmd="mv  D* "+eventDir
        os.system(cmd)
        with open(filename,'r') as eventLstFile:
            eventLst=eventLstFile.readlines()
        lineIndex=-1
        eventIndex=0
        indexLst=[i for i in range(10000)]
        for line in eventLst:
            lineIndex=lineIndex+1
            if line[0]!='J':
                continue
            indexLst[eventIndex]=lineIndex
            eventIndex=eventIndex+1
        for eventName in os.listdir(eventDir):
            try:
                event=eventDir+eventName+'/'
                eventData=event+eventName+'.evt'
                eventCh=event+eventName+'.ch'
                eventInfo=event+eventName+'.txt'
                event2=eventDir2+eventName[1:7]+'/'+eventName+'/'
                eventPhaseFile=eventDir2+eventName[1:7]+'/'+eventName+'/phaseLst' 
                if os.path.exists(event2):
                    1
                else:
                    os.system("mkdir -p "+event2)
                    os.system("cp "+eventInfo+" "+event2+"/")
                win32.extract_sac(eventData, eventCh, outdir=event)
                with open(eventInfo,'r',encoding="ISO-8859-1") as info:
                    dateS=datetime.strptime(info.readline()[13:32],"%Y/%m/%d %H:%M:%S")
                    laS=info.readline()
                    la=float(laS[11:17])
                    if laS[-1]=='S':
                        la=-la
                    loS=info.readline()
                    lo=float(loS[12:18])
                    if loS[-1]=='W':
                        lo=-lo
                eventCode='J'+dateS.strftime("%Y%m%d%H%M%S")[0:-2]
                for i in range(eventIndex):
                    line=eventLst[indexLst[i]]
                    isFind=line.find(eventCode)
                    if isFind>=0:
                        eventPhase=open(eventPhaseFile,'w')
                        index=indexLst[i]
                        eventPhase.write(eventLst[index-1]+'\n')
                        for lineSta in eventLst[index:-1]:
                            eventPhase.write(lineSta+'\n')
                            if lineSta[1]=="E":
                                break
                            if lineSta[36]==" ":
                                continue
                            if lineSta[15]!='P' or lineSta[27]!='S':
                                continue
                            sta=str(lineSta[1:7]).strip(' ')
                            timeP=datetime(int(line[1:5]),int(line[5:7]),int(line[7:9]),0\
                                ,int(lineSta[21:23]),0,int(int(lineSta[25:27])*1e4))\
                            +timedelta(hours=int(lineSta[19:21]),seconds=int(lineSta[23:25]))
                            timeS=datetime(int(line[1:5]),int(line[5:7]),int(line[7:9]),0\
                                ,int(lineSta[31:33]),0,int(int(lineSta[35:37])*1e4))\
                            +timedelta(hours=int(lineSta[19:21]),seconds=int(lineSta[33:35]))
                            compStr="ENU"
                            for c in range(3):
                                file1=event+"/"+sta+"."+compStr[c]+".SAC"
                                file2=event2+"/"+sta+"."+compStr[c]+".SAC"
                                if os.path.exists(file1):
                                    sac=read(file1)
                                    stat=sac[0].stats
                                    dTimeP=(timeP-stat.starttime._get_datetime())
                                    dTimeP=dTimeP.seconds+dTimeP.microseconds*1e-6+float(stat.sac.b)
                                    dTimeS=(timeS-stat.starttime._get_datetime())
                                    dTimeS=dTimeS.seconds+dTimeS.microseconds*1e-6+float(stat.sac.b)
                                    #print(dTimeS)
                                    sac[0].stats.sac.t0=dTimeP
                                    sac[0].stats.sac.t1=dTimeS
                                    sac.write(file2)
                        eventPhase.close()
                        break
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

