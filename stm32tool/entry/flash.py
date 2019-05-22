#!/usr/bin/env python3
import stm32tool as openmv
import argparse
from progressbar import ProgressBar, widgets


def LocalBar(buf):
    DEFAULT_WIDGETS = [buf, widgets.Bar(marker='#', left='[', right=']'), widgets.Percentage()]
    prog = ProgressBar(term_width=56+len(buf), widgets=DEFAULT_WIDGETS, left_justify=False)
    return prog

def main():
    MAX_BUF_SIZE = 64
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('rb'), help='image file')
    args = parser.parse_args()

    while True:
        while not openmv.get_openmv_port():
            pass

        device_name = openmv.get_openmv_port()
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
    while openmv.get_openmv_port() != device_name:
        pass
    boot = openmv.OpenMV()
    if not boot.connect():
        exit()
    sect = boot.bootloader_flash()
    prog = LocalBar('start erase flash: ')
    for i in prog(range(sect[1], sect[2]+1)):
        boot.flash_erase(i)

    data = args.file.read()

    # write flash
    l, r = divmod(len(data), MAX_BUF_SIZE-4)
    prog = LocalBar('start download image: ')
    for i in prog(range(l)):
        boot.flash_write(data[(MAX_BUF_SIZE-4)*i: (MAX_BUF_SIZE-4)*(i+1)])

    boot.flash_write(data[(MAX_BUF_SIZE-4)*l:])
    # jump to openmv
    boot.bootloader_reset()
    print('flash success')
