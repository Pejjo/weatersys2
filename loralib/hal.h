#ifndef HopeDuino_hal_h

        #define HopeDuino_hal_h

	#include<bcm2835.h>

        #ifdef FTDI_SPI
                #define ClrPOR()
		#define SetPOR()
		#define POROut()
                #define PORIn()
                #define DIO0In()
		#define _delay_ms bcm2835_delay 
		#define _delay_us bcm2835_delayMicroseconds
		#define DIO0_H() Spi.bSpiChkInt()
	#endif
#endif

