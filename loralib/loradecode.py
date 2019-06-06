import rfm
import time
import re

matchstrs=[r'(A):([0-9A-Fa-f]{2})=([0-9A-Fa-f]{2}),([0-9A-Fa-f]{16})',
           r'(B):([0-9A-Fa-f]{2})=([0-9A-Fa-f]{2})([0-9A-Fa-f]{2}),(\d{4})',
           r'(Y):([0-9A-Fa-f]{2})=([0-9A-Fa-f]{2}),([0-9A-Fa-f]{4})([0-9A-Fa-f]{2})',
           r'(Z):([0-9A-Fa-f]{2})=([0-9A-Fa-f]{2}),([0-9A-Fa-f]{4})']

resetcause=['PORF','EXTRF','BORF','WDRF','PDIRF','SRF']

class loradecode:

    def __init__(self):
        self.classname="lora"
        self.dev = rfm.init() # radio intsance
	self.lastrx=0
	self.regexps=[]
	for expr in matchstrs:
            self.regexps.append(re.compile(expr))

    def getraw(self):
        return self.rfm.poll()

    def getreset(self,hexcode):
        msk=1
	rst=[]
        for i in range(0,8):
            if (hexcode&msk==msk):
		rst.append(resetcause[i])
            msk=msk<<1
        rststr=' '.join(rst)
        return(rststr)

    def decodeA(self, match):
        response={'token':'A', 'class':self.classname}
        response['node']=int(match[1],16)
        response['sensor']=int(match[2],16)
	response['id']=match[3] # Keep this as string
        return response

    def decodeB(self, match):
        response={'token':'B', 'class':self.classname}
        response['node']=int(match[1],16)
        response['sensor']=int(match[2],16)
	response['cycle']=int(match[3],16)
        response['temp']=int(match[4],10)/10.0
        return response

    def decodeY(self, match):
        response={'token':'Y', 'class':self.classname}
        response['node']=int(match[1],16)
        response['reset']=self.getreset(int(match[2],16))
        response['sleeptime']=int(match[3],16)
        response['nosensors']=int(match[4],16)
        return response

    def decodeZ(self, match):
        response={'token':'Z', 'class':self.classname}
        response['node']=int(match[1],16)
        response['reset']=self.getreset(int(match[2],16))
        response['battery']=int(match[3],16)/204.7
        return response

    def poll(self):
        rxb, rxt=rfm.poll()
	result=[]
        if rxb>0:
           for reg in self.regexps:
               m=reg.match(rxt)
               if m:
                   matchgroup=m.groups()
                   if matchgroup[0]=='A':
                       result=self.decodeA(matchgroup)
                   elif matchgroup[0]=='B':
                       result=self.decodeB(matchgroup)
                   elif matchgroup[0]=='Y':
                       result=self.decodeY(matchgroup)
                   elif matchgroup[0]=='Z':
                       result=self.decodeZ(matchgroup)
        return rxb, result


