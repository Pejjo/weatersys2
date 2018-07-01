from distutils.core import setup, Extension

rfmmodule = Extension('rfm',
                    include_dirs = ['/usr/local/include',],
                    libraries = ['bcm2835'],
                    library_dirs = ['/usr/local/lib','./'],
                    sources = ['lora_py.cpp','HopeDuino_LoRa.cpp','raspi_SPI.cpp'])

setup (name = 'rfmloralib',
       version = '1.0',
       description = 'RFM96 LoRa interface',
       ext_modules = [rfmmodule])
