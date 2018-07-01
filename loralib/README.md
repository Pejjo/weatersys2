# HopeDuino for Raspberry PI

Very simple python interface for HopeDuino LoRa running on a Raspberry Pi

## Getting Started

#import rfm

rfm.init()

print (rfm.poll())


### Prerequisites

* You need the bcm2835 c-library installed.
* Radio module connected to the Raspberry SPI-interface. I use my rfpi module. (https://github.com/Pejjo/rfpi)

### Installing

sudo python setup.py install

to compile the code.

sudo python test.py

for a short demo.

## Built With

* [bcm2835 1.55](http://www.airspayce.com/mikem/bcm2835/index.html) - The bcm2335 C-library
* [pyhton 2.7.13](https://www.python.org/) - Python

## Contributing

Feel free

## Authors

* Per Pejjo Johansson - Just a quick work to get my system up and running.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

This project uses inspiration from
* Hoperf's HopeDuino code (http://www.hoperf.com)
* lupuen's LoraArduino (https://github.com/lupyuen/LoRaArduino)
