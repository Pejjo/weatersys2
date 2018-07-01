from smbus2 import SMBus, i2c_msg
import time

DEVICE_BUS = 1
DEVICE_ADDR = 0x27

#bus = SMBus(DEVICE_BUS)
#bus.write_byte(DEVICE_ADDR,0xAC)

classname="npa201"
dev =  SMBus(DEVICE_BUS)
dev.write_byte(DEVICE_ADDR,0xAC)
retval={'token':'', 'class':classname}
print(DEVICE_ADDR)
read = i2c_msg.read(DEVICE_ADDR, 5)
dev.i2c_rdwr(read)
npa_data=list(read)
# Start new conversion
time.sleep(1)
dev.write_byte(DEVICE_ADDR,0xAC)
#       print (npa_data)
npa_status=npa_data[0]
npa_pres=((npa_data[1]<<8)+npa_data[2])
npa_temp=((npa_data[3]<<8)+npa_data[4]) 

#       print (npa_status, npa_pres, npa_temp)
real_pres=1.0*npa_pres/65535*(1260-260)+260
real_temp=1.0*npa_temp/65535*(85+40)-40

retval['pressure']=real_pres
retval['temp']=real_temp
retval['status']=npa_status

real_status=""

if (npa_status&0x40):
            real_status+="Pwr"
if (npa_status&0x20):
            real_status+="Bsy"
if (npa_status&0x18==0):
            real_status+="Norm"
else:
            real_status+="Cmd"
if (npa_status&0x04):
            real_status+="Merr"
if (npa_status&0x02):
            real_status+="Dcor"
if (npa_status&0x01):
            real_status+="Asat"
retval['statustext']=real_status





x=npa201()
while (1):
  print(x.poll())
  time.sleep(5)
