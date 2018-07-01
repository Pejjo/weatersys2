//==============================================================================
//    S E N S I R I O N   AG,  Laubisruetistr. 50, CH-8712 Staefa, Switzerland
//==============================================================================
// Project   :  SHT2x Sample Code (V1.2)
// File      :  main.c
// Author    :  MST
// Controller:  NEC V850/SG3 (uPD70F3740)
// Compiler  :  IAR compiler for V850 (3.50A)
// Brief     :  This code is an example how to implement basic commands for the
//              humidity and temperature sensor SHT2x.
//              Due to compatibility reasons the I2C interface is implemented
//              as "bit-banging" on normal I/O's. This code is written for an
//              easy understanding and is neither optimized for speed nor code
//              size.
//
// Porting to a different microcontroller (uC):
//   - define the byte-order for your uC (e.g. little endian) in typedefs.h
//   - definitions of basic types may have to be changed  in typedefs.h
//   - change the port functions / definitions for your uC    in I2C_HAL.h/.c
//   - adapt the timing of the delay function for your uC     in system.c
//   - adapt the HW_Init()                                    in system.c
//   - change the uC register definition file <io70f3740.h>   in system.h
//==============================================================================
//Revision:
//V1.1 Initial Version for SHT2x B-Samples
//V1.2 Changed calculation formula in SHT2x.c for C-Samples
//---------- Includes ----------------------------------------------------------
#include "SHT2x.h"
//header file for SHT2x functions
#include "I2C_HAL.h"
//header file for I2C hardware abstraction
//#include "DisplayDip204.h"
//header file for display functions
//#include "System.h"
//header file for system settings
#include <stdio.h>
//header file standard input / output functions
//==============================================================================
int main()
//==============================================================================
{  
// variables
  int  error = 0;              
//variable for error code. For codes see system.h
  int  userRegister;           
//variable for user register
  int   endOfBattery;           
//variable for end of battery
  int sRH;                    
//variable for raw humidity ticks
  float   humidityRH;             
//variable for relative humidity[%RH] as float
  char humitityOutStr[21];     
//output string for humidity value
  int sT;                     
//variable for raw temperature ticks
  float   temperatureC;           
//variable for temperature[°C] as float 
 char temperatureOutStr[21];
//output string for temperature value
  int  SerialNumber_SHT2x[8];  
//64bit serial number
  Init_HW();                   
//initializes Hardware (osc, watchdog,...)
  I2c_Init();                  
//initializes uC-ports for I2C
//  DisplayInit();          
//initializes LCD
//  DisplayEnableBacklight();    
//enable LCD backlight
//  DisplayWriteString(0,0," SHT2x Sample Code "); 
//write project title on LCD
  DelayMicroSeconds(15000);    
//wait for sensor initialization t_powerUp (15ms)
//note: The following code segments show how to use the different functions
//      of SHT2x. The loop does not show a typical sequence in an application
while(1)
  { error = 0;                                       
// reset error status
// --- Reset sensor by command ---
    error |= SHT2x_SoftReset();
// --- Read the sensors serial number (64bit) ---
    error |= SHT2x_GetSerialNumber(SerialNumber_SHT2x);
// --- Set Resolution e.g. RH 10bit, Temp 13bit ---
    error |= SHT2x_ReadUserRegister(&userRegister);  
//get actual user reg
    userRegister = (userRegister & ~SHT2x_RES_MASK) | SHT2x_RES_10_13BIT;
    error |= SHT2x_WriteUserRegister(&userRegister); 
//write changed user reg
// --- measure humidity with "Hold Master Mode (HM)"  ---
    error |= SHT2x_MeasureHM(HUMIDITY, &sRH);
// --- measure temperature with "Polling Mode" (no hold master) ---
    error |= SHT2x_MeasurePoll(TEMP, &sT);
// -- calculate humidity and temperature --
    temperatureC = SHT2x_CalcTemperatureC(sT.u16);
    humidityRH   = SHT2x_CalcRH(sRH.u16);
// --- check end of battery status (eob)---
// note: a RH / Temp. measurement must be executed to update the status of eob
    error |= SHT2x_ReadUserRegister(&userRegister);  
//get actual user reg
   if( (userRegister & SHT2x_EOB_MASK) == SHT2x_EOB_ON ) 
	endOfBattery = true;
   else
  	endOfBattery = false;
//-- write humidity and temperature values on LCD --
    printf("Humidity RH:%6.2f %% ",humidityRH);
    printf("Temperature:%6.2fC",temperatureC);
//-- write error or low batt status un LCD --
    if (error != 0)
       printf("Error occurred");
    else if (endOfBattery) 
       printf("Low Batt");
       
    DelayMicroSeconds(300000);     
  }
}

