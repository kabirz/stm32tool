#!/usr/bin/env python3
import stm32tool as openmv
import argparse
from progressbar import ProgressBar

def main():
    MAX_BUF_SIZE = 64
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=argparse.FileType('rb'), default='firmware/OPENMV3/firmware.bin', help='image file')
    args = parser.parse_args()

    while True:
        while not openmv.get_openmv_port():
            pass

        boot = openmv.OpenMV()
        if not boot.connect():
            exit()
        if boot.bootloader_start():
            break
        else:
            boot.reset()
            print('reboot to bootloader')
            while openmv.get_openmv_port():
                pass

    # erase flash
    sect = boot.bootloader_flash()
    print('start erase flash')
    prog = ProgressBar()
    for i in prog(range(sect[1], sect[2]+1)):
        boot.flash_erase(i)
     
    data = args.file.read()

    # write flash
    l, r = divmod(len(data), MAX_BUF_SIZE-4)
    print('start download image')
    prog = ProgressBar()
    for i in prog(range(l)):
        boot.flash_write(data[(MAX_BUF_SIZE-4)*i: (MAX_BUF_SIZE-4)*(i+1)])

    boot.flash_write(data[(MAX_BUF_SIZE-4)*l:])
    # jump to openmv
    boot.bootloader_reset()
    print('flash success')
