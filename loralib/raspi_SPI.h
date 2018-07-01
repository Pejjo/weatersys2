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
 *
 * website: www.HopeRF.com
 *          www.HopeRF.cn    
 */

/*! 
 * file       HopeDuino_SPI.cpp
 * brief      for HopeRF's EVB to use Hardware SPI
 * hardware   HopeRF's EVB
 *            
 *
 * version    1.1
 * date       Jan 15 2015
 * author     QY Ruan
 */


#ifndef HopeDuino_SPI_h
	#define HopeDuino_SPI_h

	#include <bcm2835.h>

	#ifndef nSS_Value
		#warning "Does not define nSS_Value/nSS_Port/nSS_Dir! Default setting PortB_4 for nSS."
		#define	nSS_Value	BCM2835_SPI_CS1
		#define RPI_GPIO_INT	25
		#define RPI_GPIO_RST	22
		#define RPI_GPIO_RED	23
		#define RPI_GPIO_BLU	24
        #elif

		#error fix nSS value
	#endif
	
	#ifndef	byte
		typedef unsigned char byte;
	#endif
	
	#ifndef word
		typedef unsigned int  word;
	#endif

        #define SetnSS()
        #define ClrnSS()
	#define ClrPOR() Spi.vSetRst(1)
	#define SetPOR() Spi.vSetRst(0)
	#define PORIn()
	#define POROut()
	#define DIO0In() 
	#define DIO0_H() Spi.bGetInt()
	#define _delay_ms(x) bcm2835_delay(x)
	#define _delay_us(x) bcm2835_delayMicroseconds(x)

	#define LED_RED	0x01
	#define LED_BLU	0x02
	#define LED_OFF	0x00

	#define IOERR	0x01

	class spiClass
	{
	 public:
		int iSpiInit(void);				/** initialize hardware SPI config, SPI_CLK = Fcpu/4 **/	
	 	void vSpiWrite(word dat);			/** SPI send one word **/
		byte bSpiRead(byte addr);			/** SPI read one byte **/
		void vSpiBurstWrite(byte addr, byte *ptr, byte length);	/** SPI burst send N byte **/
		void vSpiBurstRead(byte addr, byte *ptr, byte length);	 	/** SPI burst rend N byte **/
		void vSetRst(byte state);	// Set reset IO-line
		byte bGetInt(void);		// Get Interupt IO-line
		void vSetLed(int state);	// Set Leds
	 private:
	 	byte bSpiTransfer(byte dat);		/**	SPI send/read one byte **/
	};

#else
	#warning "HopeDuino_SPI.h have been defined!"

#endif
