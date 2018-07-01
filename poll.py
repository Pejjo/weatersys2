import schedule
import time
import loralib.loradecode
import npa201.npa201
import sht21.sht21
import pjohat.pjohat
import sysmon.sysmon
import mqttlib.mqttclass
import time
import ConfigParser
import os
from smbus2 import SMBus
import logging
import logging.handlers
import argparse
import socket
import sys

### Configure logging

# Defaults
LOG_FILENAME = "/var/log/weathersys/pjohat.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print ("poll.py started. Logging to "+LOG_FILENAME)

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Thunder data poller")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)


### End logging

### Display message


def sendmsg(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(msg, (UDP_IP, UDP_PORT))
    sock.close()


### Device init
#open I2C
DEVICE_BUS = 1

#Create class objects
hat = pjohat.pjohat.pjohat()
bus = SMBus(DEVICE_BUS)

lora=loralib.loradecode.loradecode()

npa=npa201.npa201.npa201(bus)

sht21=sht21.sht21.SHT21(bus)

sysinfo=sysmon.sysmon.sysmon()

def mqled(value):
   global ledtimer
   if value>0:
      hat.setled(0x02)
      ledtimer=1
   elif value<0:
      hat.setled(0x01)
      ledtimer=10

def mqlog(message,level):
   if level==0:
      sendmsg(message)
   else:
      logger.log(level,message)

mqttc = mqttlib.mqttclass.MyMQTTClass(status_cb=mqled, log_cb=mqlog)

### End device

#Globals

lastdio=0
lastkey=0
ledtimer=0

#Parse args

#Open Config
cfgname=os.path.splitext(__file__)[0]+".cfg"

print "Reading default config file " + cfgname

config = ConfigParser.ConfigParser({'port': '1883', 'client_name':None})
config.read(cfgname)

verbose=True

# Helper functions

def poll_npa():
   retval=npa.poll()
   cfg=retval['class']
   if config.has_section(cfg):
      try:
         if config.has_option(cfg,'topic_temp'):
            topic_temp=config.get(cfg, 'topic_temp')
            mqttc.publish_msg(topic_temp,retval['temp'])
         if config.has_option(cfg,'topic_baro'):
            topic_press=config.get(cfg, 'topic_baro')
            mqttc.publish_msg(topic_press,retval['pressure'])
         if config.has_option(cfg,'topic_stat'):
            topic_press=config.get(cfg, 'topic_stat')
            mqttc.publish_msg(topic_press,retval['status'])

      except ConfigParser.Error as err:
         print("Config error, ",err)
   else:
      if verbose:
	print("Class {} is not configured".format(cfg))

def poll_sht():
   retval=sht21.get_digest()
   cfg=retval['class']
   if config.has_section(cfg):
      try:
         if config.has_option(cfg,'topic_temp'):
            topic_temp=config.get(cfg, 'topic_temp')
            mqttc.publish_msg(topic_temp,retval['temp'])
         if config.has_option(cfg,'topic_humi'):
            topic_temp=config.get(cfg, 'topic_humi')
            mqttc.publish_msg(topic_temp,retval['humi'])
         if config.has_option(cfg,'topic_stat'):
            topic_temp=config.get(cfg, 'topic_stat')
            mqttc.publish_msg(topic_temp,retval['status'])

      except ConfigParser.Error as err:
         print("Config error, ",err)
   else:
      if verbose:
        print("Class {} is not configured".format(cfg))


def poll_radio():
   rxb,result=lora.poll()
   if rxb>0:
      print(result," (",rxb," byte)")

def poll_cpu():
   retval=sysinfo.get_cpu_info()
   cfg=retval['class']
   if config.has_section(cfg):
      try:
         if config.has_option(cfg,'topic_cpu_temp'):
            topic_temp=config.get(cfg, 'topic_cpu_temp')
            mqttc.publish_msg(topic_temp,retval['temp'])
         if config.has_option(cfg,'topic_cpu_load'):
            topic_temp=config.get(cfg, 'topic_cpu_load')
            mqttc.publish_msg(topic_temp,retval['load'])

      except ConfigParser.Error as err:
         print("Config error, ",err)
   else:
      if verbose:
        print("Class {} is not configured".format(cfg))

def poll_ram():
   retval=sysinfo.get_ram_info()

   cfg=retval['class']
   print(retval)
   if config.has_section(cfg):
      try:
         if config.has_option(cfg,'topic_ram_used'):
            topic_temp=config.get(cfg, 'topic_ram_used')
            mqttc.publish_msg(topic_temp,int(retval['used']))
         if config.has_option(cfg,'topic_ram_total'):
            topic_temp=config.get(cfg, 'topic_ram_total')
            mqttc.publish_msg(topic_temp,int(retval['total']))
         if config.has_option(cfg,'topic_ram_free'):
            topic_temp=config.get(cfg, 'topic_ram_free')
            mqttc.publish_msg(topic_temp,int(retval['free']))

      except ConfigParser.Error as err:
         print("Config error, ",err)
   else:
      if verbose:
        print("Class {} is not configured".format(cfg))

def poll_dsk():
   retval=sysinfo.get_disk_info()
   cfg=retval['class']
   print(retval)
   if config.has_section(cfg):
      try:
         if config.has_option(cfg,'topic_disk_used'):
            topic_temp=config.get(cfg, 'topic_disk_used')
            mqttc.publish_msg(topic_temp,int(retval['used']))
         if config.has_option(cfg,'topic_disk_total'):
            topic_temp=config.get(cfg, 'topic_disk_total')
            mqttc.publish_msg(topic_temp,int(retval['total']))
         if config.has_option(cfg,'topic_disk_free'):
            topic_temp=config.get(cfg, 'topic_disk_free')
            mqttc.publish_msg(topic_temp,int(retval['free']))

      except ConfigParser.Error as err:
         print("Config error, ",err)
   else:
      if verbose:
        print("Class {} is not configured".format(cfg))

#Schedule

schedule.every(30).seconds.do(poll_npa)
schedule.every(30).seconds.do(poll_sht)
schedule.every(1).hours.do(poll_cpu)
schedule.every(1).hours.do(poll_ram)
schedule.every(1).hours.do(poll_dsk)

mqttc.setup_security('/usr/local/harvest/cert/ca.crt', certfile='/usr/local/harvest/cert/wthr.crt', keyfile='/usr/local/harvest/cert/wthr.key', username='wthr', password='FsZ2HZq6chkQGkLnZQ')
mqttc.setup_connection('194.218.40.18',8883,60)

mqttc.publish_msg('topic','startup')


# Main loop
while True:
  # Periodic tasks
  rc = mqttc.loop()

  schedule.run_pending()

  # Check keys
  key=hat.getkeyevt()
  if (key^lastkey):
      if config.has_section('keys'):
         try:
            if (key^lastkey)==0x01:
               if config.has_option('keys','topic_key1'):
                  topic_temp=config.get('keys', 'topic_key1')
                  mqttc.publish_msg(topic_temp,((key&0x01)==0x01),retain=True)
            if (key^lastkey)==0x02:
               if config.has_option('keys','topic_key2'):
                  topic_temp=config.get('keys', 'topic_key2')
                  mqttc.publish_msg(topic_temp,((key&0x02)==0x02),retain=True)

         except ConfigParser.Error as err:
            print("Config error, ",err)
      else:
         if verbose:
           print("Class {} is not configured".format('keys'))
      print("Key: ",key, " (was: ", lastkey, " )")
      lastkey=key

  dio=hat.getdioevt()
  if (dio^lastdio):
      if config.has_section('dios'):
         try:
            if (dio^lastdio)==0x01:
               if config.has_option('dios','topic_dio1'):
                  topic_temp=config.get('dios', 'topic_dio1')
                  mqttc.publish_msg(topic_temp,((dio&0x01)==0x01),retain=True)
            if (dio^lastdio)==0x02:
               if config.has_option('dios','topic_dio2'):
                  topic_temp=config.get('dios', 'topic_dio2')
                  mqttc.publish_msg(topic_temp,((dio&0x02)==0x02),retain=True)

         except ConfigParser.Error as err:
            print("Config error, ",err)
      else:
         if verbose:
           print("Class {} is not configured".format('keys'))
      print("Key: ",dio, " (was: ", lastdio, " )")
      lastdio=dio

  # Check radio
  poll_radio()

  # Clear leds if set
  if ledtimer>0:
     ledtimer-=1
  if ledtimer==0:
     hat.setled(0)
     ledtimer=-1

  # Sleep
  time.sleep(0.1)


