# Makefile
# Sample for raw example on Raspberry Pi
# Caution: requires bcm2835 library to be already installed
# http://www.airspayce.com/mikem/bcm2835/

CC       = g++
CFLAGS   = -std=c++11 -DFTDI_SPI -D__BASEFILE__=\"$*\" -fpermissive
CXXFLAGS = -Wall -O3 -g 
LIBS     = -lbcm2835
LMICBASE = ./
INCLUDE  = -I$(LMICBASE) 

all: lorarx

lora_rx.o: lora_rx.cpp
				$(CC) $(CFLAGS) -c lora_rx.cpp $(INCLUDE)

lora_tx.o: lora_tx.cpp
				$(CC) $(CFLAGS) -c lora_tx.cpp $(INCLUDE)

HopeDuino_LoRa.o: HopeDuino_LoRa.cpp
				$(CC) $(CFLAGS) -c HopeDuino_LoRa.cpp $(INCLUDE)

raspi_SPI.o: raspi_SPI.cpp
				$(CC) $(CFLAGS) -c raspi_SPI.cpp $(INCLUDE)

lorarx: lora_rx.o HopeDuino_LoRa.o raspi_SPI.o
				$(CC) $^ $(LIBS) -o lorarx

loratx: loea_tc.o HopeDuino_LoRa.o raspi_SPI.o 
				$(CC) $^ $(LIBS) -o loratx

clean:
				rm -rf *.o lorarx
