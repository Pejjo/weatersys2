#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation

# This example shows how you can use the MQTT client in a class.

#import context  # Ensures paho is in PYTHONPATH
import ssl
import paho.mqtt.client as mqtt

def none(self, level):
       pass

def console(self, message, level):
      print(message)


class MyMQTTClass(mqtt.Client):

    def __init__(self, client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp", status_cb=none, log_cb=console):
       self.statuscb=status_cb
       self.logcb=log_cb 
       super(MyMQTTClass, self).__init__(client_id, clean_session, userdata, protocol, transport)

    def on_connect(self, mqttc, obj, flags, rc):
        self.statuscb(100)
        self.logcb("Con "+str(rc),0)

    def on_disconnect(self, mqttc, userdata, rc):
        self.statuscb(-100)
        self.logcb("Dis "+str(rc),0)

    def on_message(self, mqttc, obj, msg):
        self.statuscb(1)
        self.logcb("Msg "+msg.topic+" "+str(msg.qos)+" "+str(msg.payload),0)

    def on_publish(self, mqttc, obj, mid):
        self.statuscb(2)
        self.logcb("Pub "+str(mid),0)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.statuscb(10)
        self.logcb("Sub "+str(mid)+" "+str(granted_qos),0)

    def on_unsubscribe(self, mqttc, userdata, mid):
        self.statuscb(-10)
        self.logcb("Uns "+str(mid),0)

    def on_log(self, mqttc, obj, level, string):
        self.logcb(string, level)

    def setup_security(self, cafile, certfile=None, keyfile=None, username=None, password=None):
        self.tls_set(cafile, certfile=certfile, keyfile=keyfile,
         cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
        self.tls_insecure_set(True)
        self.username_pw_set(username, password=password)

    def setup_connection(self, host, port,keepalive):
        self.host=host
        self.port=port
        self.keepalive=keepalive
        self.connect(self.host, self.port, self.keepalive)

    def publish_msg(self, topic, msg, qos=1, retain=False):
        self.publish(topic, msg, qos, retain=False)

    def run(self):
#        self.connect("m2m.eclipse.org", 1883, 60)
        self.subscribe("#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.

if __name__ == "__main__":

    mqttc = MyMQTTClass()
    mqttc.setup_security('/usr/local/harvest/cert/ca.crt', certfile='/usr/local/harvest/cert/wthr.crt', keyfile='/usr/local/harvest/cert/wthr.key', username='wthr', password='FsZ2HZq6chkQGkLnZQ')
    mqttc.setup_connection('194.218.40.18',8883,60)
    rc = mqttc.run()

#    print("rc: "+str(rc))

# mqttc.publish(mq_topic+'/addr', adr)

#cfgname=os.path.splitext(__file__)[0]+".cfg"

#print "Reading default config file " + cfgname

#config = ConfigParser.ConfigParser({'baud': '115200', 'port': '1883', 'defaulttopic':'sensors/'})
#config.read(cfgname)

#ser=serial.Serial(config.get("harvester", "serial"), config.get("harvester", "baud"), timeout=0)

#mqttc.connect(config.get("harvester", "server"), config.get("harvester", "port"), 60)

##default_topic=config.get("harvester", "defaulttopic")

##rc = mqttc.run()
#print("rc: "+str(rc))
