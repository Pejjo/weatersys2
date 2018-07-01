import time
import RPi.GPIO as GPIO

LED_RED=20
LED_GRN=21
DIO_1  =16
DIO_2  =26
BTN_1  =27
BTN_2  =18

class pjohat:

    def __init__(self):
        self.classname="pjohat"
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_RED,GPIO.OUT)
        GPIO.setup(LED_GRN,GPIO.OUT)
        GPIO.setup(DIO_1,GPIO.IN)
        GPIO.setup(DIO_2,GPIO.IN)
        GPIO.setup(BTN_1,GPIO.IN)
        GPIO.setup(BTN_2,GPIO.IN)
        GPIO.add_event_detect(BTN_1, GPIO.FALLING, bouncetime=200)
        GPIO.add_event_detect(BTN_2, GPIO.FALLING, bouncetime=200)
        GPIO.add_event_detect(DIO_1, GPIO.FALLING, bouncetime=200)
        GPIO.add_event_detect(DIO_2, GPIO.FALLING, bouncetime=200)

    def getkey(self):
        """ Read key directly """
	retval=0
        if (GPIO.input(BTN_1)==0):
           retval|=0x01
        if (GPIO.input(BTN_2)==0):
           retval|=0x02
        return (retval)

    def getdio(self):
        """ Read dio direcly """
        retval=0
        if (GPIO.input(DIO_1)==0):
           retval|=0x01
        if (GPIO.input(DIO_2)==0):
           retval|=0x02
        return (retval)

    def getkeyevt(self):
        """ Read event buffer that is set on input edge """
        retval=0
        if (GPIO.event_detected(BTN_1)):
           retval|=0x01
        if (GPIO.event_detected(BTN_2)):
           retval|=0x02
        return(retval)

    def getdioevt(self):
        """ Read event buffer that is set on input edge """
        retval=0
        if (GPIO.event_detected(DIO_1)):
           retval|=0x01
        if (GPIO.event_detected(DIO_2)):
           retval|=0x02
        return(retval)

    def setled(self, led):
	if (led&0x01):
           GPIO.output(LED_RED,GPIO.HIGH)
	else:
           GPIO.output(LED_RED,GPIO.LOW)

	if (led&0x02):
           GPIO.output(LED_GRN,GPIO.HIGH)
	else:
           GPIO.output(LED_GRN,GPIO.LOW)
    def __exit__(self):
        pass

    def __enter__(self):
        return self


if __name__ == "__main__":
#    try:
        with pjohat() as hat:
         while(True):
            x=hat.getkey()
            if (x&1):
               hat.setled(1)
            if (x&2):
               hat.setled(2)
            if not (x):
               hat.setled(0)
            else:
               print("Key: ",hex(x))

            y=hat.getdio()
            if(y):
              print("Dio: ",hex(y))
            time.sleep(0.1)
#    except:
#	print("err<")
