# Stm32 Tool
## Dependences
- pyserial
- pygame
- numpy
- Pillow
- pyusb
- progressbar
## Install Module
```bash
pip3 install stm32tool [--user]
```
or
```bash
pip3 install git+https://github.com/kabirz/stm32tool [--user]
```
## Generate dfu image
```bash
mkdfu <-b 0x08000000:binary image file>  <dfu image file>
```
## Download Firmware
- dfu mode
```bash
pydfu <-u dfu file>
```
- openmv normal mode
```bash
openmvflash <firmware image binary file>
```
## Openmv Camera Preiview
```bash
openmvview [-f micropython script]
```

## Stm32 Isp Flash Firmware
```bash
stm32isp <firmware image binary file>
```

## Get OpenMV Borad Info
```bash
openmvdevice
```
