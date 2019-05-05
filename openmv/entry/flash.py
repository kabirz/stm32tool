#!/usr/bin/env python3
import openmv
import argparse


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
    for i in range(sect[1], sect[2]+1):
        boot.flash_erase(i)
        hper = int(float((i-sect[1])/(sect[2]-sect[1]))*100)
        print('\rflash erase:[{}{}] {}%'.format('=' * (hper//4), ' ' * (25-hper//4), hper), end='')
    data = args.file.read()

    # write flash
    l, r = divmod(len(data), MAX_BUF_SIZE-4)
    print('\nstart download image')
    for i in range(l):
        boot.flash_write(data[(MAX_BUF_SIZE-4)*i: (MAX_BUF_SIZE-4)*(i+1)])
        hper = int(float(i)/l*100)
        print('\rflash write:[{}{}] {}%'.format('=' * (hper//4), ' ' * (25-hper//4), hper), end='')
    boot.flash_write(data[(MAX_BUF_SIZE-4)*l:])
    print('\rflash write:[{}{}] {}%'.format('=' * 25, ' ' * (25-25), 100))
    # jump to openmv
    boot.bootloader_reset()
    print('flash success')
