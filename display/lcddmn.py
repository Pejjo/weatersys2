#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
LCD daemon for weather project
"""

import time
import datetime
from luma.core.render import canvas
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306
import fcntl
import struct
import threading
from Queue import Queue
import socket
import time
import sys
import re
import signal
import logging
import logging.handlers


LOG_FILENAME = "/var/log/weathersys/lcddmn.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
LOG_LEVEL = logging.DEBUG

print("Logging to file "+LOG_FILENAME)

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


messages = Queue()

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

stopped=False

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def networker():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        messages.put(data)

def stop(sig, frame):
    global stopped
    stopped=True
 

def main():
    global stopped
    auxline=""
    logts = datetime.datetime.now()
    logmsg = ""
    logtme = ""

    t = threading.Thread(target=networker, name='networker')
    t.daemon = True
    t.start()

    today_last_time = "Unknown"
    scpos=0
    dir=-1




    while not stopped:
        now = datetime.datetime.now()
        today_date = now.strftime("%d %b %y")
        today_time = now.strftime("%H:%M:%S")
 
        if today_time != today_last_time:
            today_last_time = today_time
            myip = get_ip_address('eth0')  # '192.168.0.110'
            if not messages.empty():
                msg=messages.get()
                messages.task_done()
		try:
                    if (msg[0]=='<'):
			pattern=re.compile("^<\d{3}>(?P<month>[a-zA-Z]{3})\s+(?P<day>\d\d?)\s(?P<hour>\d\d)\:(?P<minute>\d\d):(?P<second>\d\d)(?:\s(?P<suppliedhost>[a-zA-Z0-9_-]+))?\s(?P<host>[a-zA-Z0-9_-]+)\s(?P<process>[a-zA-Z0-9\/_-]+)(\[(?P<pid>\d+)\])?:\s(?P<message>.+)$").match(msg)
                        month=datetime.datetime.strptime(pattern.group('month'), '%b').month
                        logts=datetime.datetime(now.year,month,int(pattern.group('day')),int(pattern.group('hour')),int(pattern.group('minute')),int(pattern.group('second')))
			logmsg=pattern.group('message')
                    else:
                        auxline=msg
                except:
                    logging.exception("MEssage")

            with canvas(device) as draw:
                now = datetime.datetime.now()
                today_date = now.strftime("%d %b %y")

                margin = 0

                cx = 0
                cy = 0
                width=draw.textsize(myip)[0]
                if width>device.width:
                        scpos+=dir
                        if (device.width-scpos)>width:
                              dir=1
                        if (scpos>=0):
                              dir=-1

                try:
                    if len(logmsg)>0:
                        delta=now-logts
                        if delta.days>30: # xpire after 30 days
                            logmsg=""
                            logtme=""
                        elif delta.days>0:
                            logtme="{:d}d".format(delta.days)
                        elif (delta.seconds//3600)>0:
                            logtme="{:d}h".format(delta.seconds//3600)
                        elif (delta.seconds//60)>0:
                            logtme="{:d}m".format(delta.seconds//60)
                        else:
                            logtme="{:d}s".format(delta.seconds)
                except:
                    logtme=""
                    logmsg=""
                    logging.exception("syslog")

                draw.text(((cx + margin), cy), today_time, fill="yellow")
                draw.text(((cx + margin + scpos), cy+9), myip, fill="yellow")
                draw.line([(0,21),(device.width,21)],fill="yellow",width=1)
		draw.text((cx + margin, cy+24),logtme + ':' + logmsg[:10] ,fill="yellow")
		draw.text((cx + margin, cy+33),auxline[:12] ,fill="yellow")

        time.sleep(0.1)
    with canvas(device) as draw:
        draw.text((0, 0), 'Shdn', fill="yellow")
	print ("exit")

signal.signal(signal.SIGTERM, stop)

if __name__ == "__main__":
    try:
        logger.info("lcddmn started")
#        device = get_device()

        # rev.1 users set port=0
        # substitute spi(device=0, port=0) below if using that interface
        serial = i2c(port=1, address=0x3C)

        # substitute ssd1331(...) or sh1106(...) below if using that device
        device = ssd1306(serial, height=64, width=48, rotate=1)
        device.contrast(0)

        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception("Lcddmn crash")
