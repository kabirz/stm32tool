# Openmv Tool
## Dependences
- pyserial
- pygame
- numpy
- Pillow
- pyusb
## Install Module
```bash
pip3 install git+https://github.com/kabirz/openmv --user
```
## Generate dfu image
```bash
mkdfu -b 0x08000000:openmv.bin openmv.dfu
```
## Download Firmware
- dfu mode
```bash
pydfu -u openmv.dfu
```
- normal mode
```bash
stmflash  -f firmware.bin
```
## Camera Preiview
```bash
openmvview -f python_script_file
```
