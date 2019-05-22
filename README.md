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
stmflash <firmware image file>
```
## Openmv Camera Preiview
```bash
openmvview [-f python_script_file]
```

## Stm32 isp flash firmware
```bash
stm32isp <frimware.bin>
```
