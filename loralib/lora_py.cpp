/*
 * THE FOLLOWING FIRMWARE IS PROVIDED: 
 *  (1) "AS IS" WITH NO WARRANTY; 
 *  (2) TO ENABLE ACCESS TO CODING INFORMATION TO GUIDE AND FACILITATE CUSTOMER.
 * CONSEQUENTLY, HopeRF SHALL NOT BE HELD LIABLE FOR ANY DIRECT, INDIRECT OR
 * CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING FROM THE CONTENT
 * OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE CODING INFORMATION
 * CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
 * 
 * Copyright (C) HopeRF
 * website: www.HopeRF.com
 *          www.HopeRF.cn
 *
 */

/*! 
 * file       lora_rx.ino
 * hardware   HopeDuino 
 * software   get message via HopeRF's LoRa COB, & send message to uart
 * note       can talk to HopeRF's EVB or DK demo           
 *
 * version    1.0
 * date       Jun 10 2014
 * author     QY Ruan
 */
#include <Python.h>

#include "HopeDuino_LoRa.h"
#include <stdio.h>
#include <unistd.h>

loraClass radio;

byte getstr[100];

int setup()
{ 
 int err;
 radio.Modulation     = LORA;
 radio.COB            = RFM96;
 radio.Frequency      = 434000;
 radio.OutputPower    = 17;             //17dBm OutputPower
 radio.PreambleLength = 16;             //16Byte preamble
 radio.FixedPktLength = false;          //explicit header mode for LoRa
 radio.PayloadLength  = 21;
 radio.CrcDisable     = false;
 
 radio.SFSel          = SF9;
 radio.BWSel          = BW125K;
 radio.CRSel          = CR4_5;

 err=radio.iInitialize();
 if (err)
   return err; // quit 
 radio.vGoRx();
 return err;
}

//void loop()
//{
// if(radio.bGetMessage(getstr)!=0)
//    {
//    printf("%s\n",getstr);
//    }  	
//}
 
//int main(void)
//{
//	int cnt=0;
//	fprintf(stderr, "Start\n");
//	setup();
//	fprintf(stderr, "Run\n");
//
//	while(1) {
//		
//	  loop();
//	  sleep(0.5);
//	}
//}

//extern "c" 

static PyObject *
rfm_init(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "")) /* No arguments */
        return NULL;
    if (setup()==IOERR)
    {
	PyErr_SetString(PyExc_IOError, "SPI open failed. Permission?");
        return NULL;
    }
    return Py_None;
}

//extern "c" 
static PyObject *
rfm_poll(PyObject *self, PyObject *args)
{
    const char noresponse[]="";
    int sts;

    if (!PyArg_ParseTuple(args, "")) /* No arguments */
        return NULL;

    sts=radio.bGetMessage(getstr,100);
    if (sts>0)
      return Py_BuildValue("is", sts, getstr);
    else // No data	
      return Py_BuildValue("is", sts, noresponse);
}

static PyMethodDef rfmMethods[] = {
    {"init",  rfm_init, METH_VARARGS,
     "Init radio module."},
    {"poll",  rfm_poll, METH_VARARGS,
     "Init radio module."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initrfm(void)
{
    PyObject *m;

    m = Py_InitModule("rfm", rfmMethods);
    if (m == NULL)
        return;

}


//PyErr_SetString(PyExc_IOError, "System command failed");
