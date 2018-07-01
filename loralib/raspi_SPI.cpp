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

#include "raspi_SPI.h"
/**********************************************************
**Name: 	vSpiInit
**Func: 	Init Spi Config
**Note: 	SpiClk = Fcpu/4
**********************************************************/
int spiClass::iSpiInit(void)
{
	// Init lib
	if (bcm2835_init()==0)
		return IOERR;

	//Setup SPI pins
        if (bcm2835_spi_begin()==0)
		return IOERR;

        //Set CS pins polarity to low
        bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, 0);
        bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS1, 0);

        //Set SPI clock speed
        //      BCM2835_SPI_CLOCK_DIVIDER_65536 = 0,       ///< 65536 = 262.144us = 3.814697260kHz (total H+L clock period)
        //      BCM2835_SPI_CLOCK_DIVIDER_32768 = 32768,   ///< 32768 = 131.072us = 7.629394531kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_16384 = 16384,   ///< 16384 = 65.536us = 15.25878906kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_8192  = 8192,    ///< 8192 = 32.768us = 30/51757813kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_4096  = 4096,    ///< 4096 = 16.384us = 61.03515625kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_2048  = 2048,    ///< 2048 = 8.192us = 122.0703125kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_1024  = 1024,    ///< 1024 = 4.096us = 244.140625kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_512   = 512,     ///< 512 = 2.048us = 488.28125kHz
        //      BCM2835_SPI_CLOCK_DIVIDER_256   = 256,     ///< 256 = 1.024us = 976.5625MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_128   = 128,     ///< 128 = 512ns = = 1.953125MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_64    = 64,      ///< 64 = 256ns = 3.90625MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_32    = 32,      ///< 32 = 128ns = 7.8125MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_16    = 16,      ///< 16 = 64ns = 15.625MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_8     = 8,       ///< 8 = 32ns = 31.25MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_4     = 4,       ///< 4 = 16ns = 62.5MHz
        //      BCM2835_SPI_CLOCK_DIVIDER_2     = 2,       ///< 2 = 8ns = 125MHz, fastest you can get
        //      BCM2835_SPI_CLOCK_DIVIDER_1     = 1,       ///< 1 = 262.144us = 3.814697260kHz, same as 0/65536

        bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_128);

        //Set SPI data mode
        //      BCM2835_SPI_MODE0 = 0,  // CPOL = 0, CPHA = 0, Clock idle low, data is clocked in on rising edge, output data$
        //      BCM2835_SPI_MODE1 = 1,  // CPOL = 0, CPHA = 1, Clock idle low, data is clocked in on falling edge, output dat$
        //      BCM2835_SPI_MODE2 = 2,  // CPOL = 1, CPHA = 0, Clock idle high, data is clocked in on falling edge, output da$
        //      BCM2835_SPI_MODE3 = 3,  // CPOL = 1, CPHA = 1, Clock idle high, data is clocked in on rising, edge output dat$
        bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);             //(SPI_MODE_# | SPI_CS_HIGH)=Chip Select active high, (SPI_MO$

        //Set with CS pin to use for next transfers
        bcm2835_spi_chipSelect(nSS_Value);

	bcm2835_gpio_fsel(RPI_GPIO_INT, BCM2835_GPIO_FSEL_INPT);		//RPI1B+ & RPi2B <<Set as input
	bcm2835_gpio_fsel(RPI_GPIO_RST, BCM2835_GPIO_FSEL_OUTP);		//RPI1B+ & RPi2B <<Set as output
	bcm2835_gpio_set_pud(RPI_GPIO_INT, BCM2835_GPIO_PUD_UP);	
	bcm2835_gpio_fsel(RPI_GPIO_BLU, BCM2835_GPIO_FSEL_OUTP);
	bcm2835_gpio_fsel(RPI_GPIO_RED, BCM2835_GPIO_FSEL_OUTP);
	return 0;
}


	//bcm2835_spi_end();

/**********************************************************
**Name: 	bSpiTransfer
**Func: 	Transfer One Byte by SPI
**Input:
**Output:  
**********************************************************/
byte spiClass::bSpiTransfer(byte dat)
{
 uint8_t data;
 data = bcm2835_spi_transfer((uint8_t)dat);
 return data;
}

/**********************************************************
**Name:	 	vSpiWrite
**Func: 	SPI Write One word
**Input: 	Write word
**Output:	none
**********************************************************/
void spiClass::vSpiWrite(word dat)
{
 char buf[2];
 buf[0]=(char)(dat>>8)|0x80;
 buf[1]=(char)dat;
 bcm2835_spi_writenb(buf,2);
}

/**********************************************************
**Name:	 	bSpiRead
**Func: 	SPI Read One byte
**Input: 	readout addresss
**Output:	readout byte
**********************************************************/
byte spiClass::bSpiRead(byte addr)
{
 char buf[2];
 buf[0]=(char)addr;
 buf[1]=0xff;

 bcm2835_spi_transfern(buf,2);
 return((byte)buf[1]);
}

/**********************************************************
**Name:	 	vSpiBurstWirte
**Func: 	burst wirte N byte
**Input: 	array length & start address & head pointer
**Output:	none
**********************************************************/
void spiClass::vSpiBurstWrite(byte addr, byte *ptr, byte length)
{
 char buf[257];
 buf[0]=(char)(addr|0x80);

 for(int x=0;x<length;x++)
 {
  buf[x+1]=(char)ptr[x];
 }

 bcm2835_spi_writenb(buf, length+1);                     //data_buffer used for tx and rx

}

/**********************************************************
**Name:	 	vSpiBurstRead
**Func: 	burst read N byte
**Input: 	array length & start address & head pointer
**Output:	none
**********************************************************/
void spiClass::vSpiBurstRead(byte addr, byte *ptr, byte length)
{
 char buf[257];
 if(length!=0)
 {
   buf[0]=(char)addr;
   bcm2835_spi_transfern(buf, length);
   for (uint8_t x=0; x<length; x++)
   {
     ptr[x]=(byte)buf[x+1];
   }
 } 		
 return;
}

void spiClass::vSetRst(byte state)
{
	bcm2835_gpio_write(RPI_GPIO_RST, state);
}

byte spiClass::bGetInt(void)
{
	byte ret;
	ret=bcm2835_gpio_lev(RPI_GPIO_INT);
	return ret;
}

void spiClass::vSetLed(int state)
{
	if (state&LED_RED)
	  bcm2835_gpio_set(RPI_GPIO_RED);
	else
	  bcm2835_gpio_clr(RPI_GPIO_RED);
	if (state&LED_BLU)
	  bcm2835_gpio_set(RPI_GPIO_BLU);
	else
          bcm2835_gpio_clr(RPI_GPIO_BLU);
}

