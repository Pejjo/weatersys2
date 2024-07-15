#! /usr/bin/python
import serial
import json
import linecache
import sys
import paho.mqtt.client as mqtt
from time import time,sleep,ctime, gmtime, strftime
import ConfigParser
import ssl
import os
from array import *
import logging
import logging.handlers
import argparse

# Defaults
LOG_FILENAME = "/var/log/weathersys/harvesttnd.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

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

def s8(value):
    return -(value & 0x80) | (value & 0x7f)

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


connected=False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global connected
    print("Connected with result code "+str(rc))
    if rc != 0:
        print("Unexpected disconnection. Reconnecting...")
        mqttc.reconnect()
	connected=False
    else :
        print "Connected successfully"
	conected=True

# The callback for when a PUBLISH message is received from the server.
def on_publish(client, userdata, mid):
        print "Publish Mid: "+ str(mid)

def on_disconnect(client, userdata, rc):
    global connected
    if rc != 0:
        print("Unexpected disconnection.")
	mqttc.reconnect()
	connected=False

def check_connection():
    if (connected==False):
        print("Reconnecing\n\r")
        mqttc.connect(config.get("harvester", "server"), config.get("harvester", "port"), 60)


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

def jsonlog(d):
	print (d)

def strlog(s):
	print (s)


cfgname=os.path.splitext(__file__)[0]+".cfg"

print "Reading default config file " + cfgname

config = ConfigParser.ConfigParser({'baud': '38400', 'port': '1883', 'defaulttopic':'sensors/'})
config.read(cfgname)


ser=serial.Serial(config.get("harvester", "serial"), config.get("harvester", "baud"), timeout=0)
print(ser.name, ' opened.\n')
mqttc = mqtt.Client(config.get("harvester", "clientname"))
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish

# the server to publish to, and corresponding port
# the server to publish to, and corresponding port

mqttc.tls_set('/usr/local/harvest/cert/ca.crt', certfile='/usr/local/harvest/cert/wthr.crt', keyfile='/usr/local/harvest/cert/wthr.key', cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)

mqttc.tls_insecure_set(True)
mqttc.username_pw_set(config.get("harvester", "user"), password=config.get("harvester", "pass"))


mqttc.connect(config.get("harvester", "server"), config.get("harvester", "port"), 60)

default_topic=config.get("harvester", "defaulttopic")

run=True
jdata = None
lsec=0

tmpsec=time()+10;

while run:
	lsec=time()
# Query collection card

	if (lsec>tmpsec):	# poll temp
		tmpsec=tmpsec+120
		ser.write("?t\r\n")
#        elif (lsec>trgsec):     # start DHT22
#                trgsec=trgsec+60
#                ser.write("*s\r\n")
#	elif (lsec>dhtsec):	# poll DHT22
#		dhtsec=dhtsec+60
#		ser.write("*r\r\n")

	line=ser.readline().strip()
# Parse input data
	crcval=1	#just set other than 1 to trap errors later
	if len(line)>0:
		splitdta=line.split(':')
		print (line)
		print (splitdta)
		if (len(splitdta)>=2): #Looks good

			try:
				if (splitdta[0]=='!T'):
					type="temp"
					crcval=0 #just a flag
					vals=array('B')
					temp=0.0
					print len(splitdta[1]) 
					if (len(splitdta[1])==4):
						for n in range(0, 4, 2):
							curbyte=int(splitdta[1][n:n+2],16)&0xff
							vals.append(curbyte)
						
						temp=(vals[1]*1.0)+(vals[0]/256.0)

						print type, vals, temp

				elif (splitdta[0]=='!E'):
					if (len(splitdta)==7):
						type="lightning"
						crcval=0 #Just flag
						timestamp=splitdta[1]
						evtype=splitdta[2]
						eventno=splitdta[3]
						distance=splitdta[5]
						energy=splitdta[6]

						print (timestamp, type, distance,energy)
					else:
						print "-ignored"

				else:
					type="err"
					print "Err2: ", line 
			except ValueError:
				PrintException()
		else:
			print "Err1: ", line

		
		if (crcval==0):	#Valid values
		
			if (config.has_section(type)):
				mq_name=config.get(type, 'name')
				mq_topic=config.get(type, 'topic')
				ctime=strftime("%Y-%m-%d %H:%M:%S", gmtime())

				if (type=='temp'):
					print( ctime, " - ", mq_name, ", ", type, ", ", temp)
					try:
						check_connection()
						mqttc.publish(mq_topic+'/name', mq_name,qos=1)
						mqttc.publish(mq_topic+'/temperature', temp,qos=1)
					except ValueError:
						PrintException()
					except:
						PrintException()
				elif (type=='lightning'):
                                        print ctime, " - ", mq_name, ", ", type, ", ", evtype, ", ",distance, " ", energy
                                        try:
						check_connection()
                                                mqttc.publish(mq_topic+'/name', mq_name, qos=1)
                                                mqttc.publish(mq_topic+'/timestamp', timestamp,qos=1)
						mqttc.publish(mq_topic+'/eventtype', evtype,qos=1)
                                                mqttc.publish(mq_topic+'/distance', distance,qos=1)
						mqttc.publish(mq_topic+'/energy', energy,qos=1)

                                        except ValueError:
                                                PrintException()
					except:
						PrintException()


			else:
				mq_name='Unknown'
				mq_topic=default_topic+adr
        try:
                mqttc.loop(2)
        except:
                PrintException()

	sleep(1)

