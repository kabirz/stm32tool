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
pip3 install stm32tool --user
```
or
```bash
pip3 install git+https://github.com/kabirz/stm32tool --user
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
## Openmv Camera Preiview
```bash
openmvview -f python_script_file
```

## Stm32 isp flash firmware
```bash
stm32isp -i frimware.bin
```
