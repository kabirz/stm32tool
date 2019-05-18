import argparse
import time
from functools import reduce
from operator import xor

import serial
from progressbar import ProgressBar
from serial.tools import list_ports

CHIPS = {
    0x410: 'STM32F10x Medium-density',
    0x411: 'STM32F2xxx',
    0x412: 'STM32F10x Low-density',
    0x413: 'STM32F40xxx/41xxx',
    0x414: 'STM32F10x High-density',
    0x416: 'STM32L1xxx6(8/B) Medium-density ultralow power line',
    0x419: 'STM3242xxx/43xxx',
    0x420: 'STM32F10x Medium-density value line',
    0x428: 'STM32F10x High-density value line',
    0x430: 'STM3210xx XL-density',
    0x444: 'STM32F03xx4/6',
    0x449: 'STM32F74xxx/75xxx',
    0x451: 'STM32F76xxx/77xxx',
    0x801: 'Wiznet W7500',
    0x11103: 'BlueNRG',
}

INIT        = 0x7F
ACK         = 0x79
NACK        = 0x1F
GETCMD      = 0x00
GETVER      = 0x01
GETID       = 0x02
READM       = 0x11
GOCMD       = 0x21
WRITEM      = 0x31
ERASEM      = 0x43 
EERASEM     = 0x44
WRITEPC     = 0x63
WRITEUPC    = 0x73
READPC      = 0x82
READUPC     = 0x92

MAX_BUF_SIZE = 0x100

CMDS = {
    0x00: 'Get Command',
    0x01: 'Get Version and Read Protection Status',
    0x02: 'Get ID',
    0x11: 'Read Memory command',
    0x21: 'Go Command',
    0x31: 'Write Memory command',
    0x43: 'Erase command',
    0x44: 'Extended Erase command',
    0x63: 'Write Protect command',
    0x73: 'Write Unrotect command',
    0x82: 'Readout Protect command',
    0x92: 'Readout Unrotect command',
}

BPS = (460800, 25600, 230400, 12800, 115200, 76800, 57600, 38400, 19200, 14400, 9600)


class Isp(object):
    def __init__(self, portname, bps=115200, timeout=5):
        self.version = None
        self.cmd = None
        self.id = None
        try:
            self.dev = serial.Serial( portname, baudrate=bps, parity='E', timeout=timeout)
        except Exception as e:
            raise e

    def _readint(self):
        val = self.dev.read()
        if len(val) == 1:
            return ord(val)
        else:
            return 0

    def _readlist(self, num):
        return list(self.dev.read(num))

    def _wait_ack(self, reset=0, info=''):
        try:
            ack = self._readint()
        except Exception:
            raise Exception('can not get ack or timeout!')
        else:
            if ack == ACK:
                return True
            else:
                if reset:
                    print('Please reset board')
                    return False
                if ack == NACK:
                    raise Exception('NACK' + info)
                else:
                    raise Exception('Unknown error: {}'.format(hex(ack)))

    def write(self, data):
        if isinstance(data, int):
            data = [data]
        self.dev.write(data)

    def writecmd_ack(self, cmd):
        self._check_cmd(cmd)
        self.write([cmd, cmd ^ 0xFF])
        self._wait_ack()

    def writeadd_ack(self, addr):
        data = addr.to_bytes(4, byteorder='big')
        self.write(data)
        self.write(reduce(xor, data))
        self._wait_ack()

    def writedat_ack(self, data):
        length = len(data) - 1
        self.write(length)
        self.write(data)
        self.write(reduce(xor, data, length))
        self._wait_ack()
    
    def _check_cmd(self, cmd):
        if self.cmd and cmd not in self.cmd:
            raise Exception('can not support cmd: {}'.format(hex(cmd)))

    def init(self):
        self.write(INIT)
        if self._wait_ack(self, 1):
            self.getCmd()
            self.getId()
            return
        print('init device timeout')
        exit()

    def getCmd(self):
        self.writecmd_ack(GETCMD)
        cmd_num = self._readint()
        self.version = hex(self._readint())
        self.cmd = self._readlist(cmd_num)
        self._wait_ack()
        if cmd_num != len(self.cmd):
            raise Exception('cmd number is error: act:{}, ep:{}'.format(
                len(self.cmd), cmd_num))

    def getVer(self):
        self.writecmd_ack(GETVER)
        self.version = hex(self._readint())
        self._readint()
        self._readint()
        self._wait_ack()

    def getId(self):
        self.writecmd_ack(GETID)
        num = self._readint()
        self.id = int.from_bytes(self.dev.read(num + 1), byteorder='big')
        self._wait_ack()

    def readmem(self, addr=0x08000000, length=0x16):
        if length > MAX_BUF_SIZE:
            raise Exception('max length is {}'.format(MAX_BUF_SIZE))
        self.writecmd_ack(READM)
        self.writeadd_ack(addr)
        self.dev.write([length-1, (length-1) ^ 0xFF])
        self._wait_ack()
        return self.dev.read(length)

    def writemem(self, data, addr=0x08000000):
        length = len(data)
        _, remain = divmod(length, 4)
        if remain:
            data += bytes([0xFF]*(4 - remain))
            length += 4 - remain
        if length > MAX_BUF_SIZE:
            raise Exception('max length is {}'.format(MAX_BUF_SIZE))
        self.writecmd_ack(WRITEM)
        self.writeadd_ack(addr)
        self.writedat_ack(data)

    def erasemem(self, all=False, pages=None):
        self.writecmd_ack(ERASEM)
        if all:
            self.dev.write([0xFF, 0x00])
            self._wait_ack()
        else:
            self.writedat_ack(pages)

    def writeProtect(self, sectors=None):
        self.writecmd_ack(WRITEPC)
        self.writedat_ack(sectors)

    def writeUnprotect(self):
        self.writecmd_ack(WRITEUPC)
        self._wait_ack()

    def readoutProtect(self, sectors=None):
        self.writecmd_ack(READPC)
        self._wait_ack()

    def readoutunprotect(self):
        self.writecmd_ack(READUPC)
        self._wait_ack()

    def go(self, addr=0x08000000):
        self.writecmd_ack(GOCMD)
        self.writeadd_ack(addr)
        print('go: {}'.format(hex(addr)))

    def info(self):
        board_info = CHIPS[self.id] if self.id in CHIPS.keys() else 'Unknown'
        print('id:{} board: {}'.format(hex(self.id), board_info))
        print('bootloader version:{}'.format(self.version))

    def commandlist(self):
        print('command list:')
        for key in self.cmd:
            if key in CMDS.keys():
                print('0x{:0>2}: \t{}.'.format(hex(key)[2:], CMDS[key]))
            else:
                raise Exception('can not support cmd {}'.format(hex(key)))

    def writebin(self, buf, addr=0x08000000):
        start = time.time()
        print('writing image...')
        size = MAX_BUF_SIZE
        sectors, remain = divmod(len(buf), size)
        prog = ProgressBar()
        for i in prog(range(sectors)):
            self.writemem(buf[i*size: (i+1)*size], addr+size*i)
        if remain:
            self.writemem(buf[sectors*size:], addr+sectors*size)
        print('The time of flash imagetime: {:.3}s'.format(time.time()-start))

    def readbuf(self, addr=0x08000000, length=MAX_BUF_SIZE):
        idx, remain = divmod(length, MAX_BUF_SIZE)
        buf = b''
        prog = ProgressBar()
        for i in prog(range(idx)):
            buf += self.readmem(addr + MAX_BUF_SIZE*i, MAX_BUF_SIZE)
        if remain:
            buf += self.readmem(addr+MAX_BUF_SIZE*idx, remain)
        return buf

    def __del__(self):
        if self.dev:
            self.dev.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--port', type=str, help='serial device name')
    parser.add_argument('-i', '--input', type=argparse.FileType(mode='rb'), help='the image binary for downloading')
    parser.add_argument('-o', '--output', type=argparse.FileType(mode='wb'), help='the image binary read from flash')
    parser.add_argument('-l', '--len', type=int, help='length of the image binary read from flash')
    parser.add_argument('-b', '--bps', default=460800, choices=BPS, type=int, help='the image binary read from flash')
    parser.add_argument('-p', '--info', action='store_true', default=True, help='boards info')
    parser.add_argument('-c', '--com', action='store_true', help='supportted command list')
    parser.add_argument('-e', '--exe', action='store_true', default=True, help='start running board')
    parser.add_argument('-a', '--addr', type=int, default=0x08000000, help='supportted command list')
    args = parser.parse_args()
    devs = list_ports.comports()
    if not args.port:
        if not devs:
            print('Please connect your board using serial')
            exit()
        elif len(devs) == 1:
            num = 0
        else:
            for i, port in enumerate(devs):
                print('{}. {}\t {}.'.format(i, port.device, port.description))
            try:
                num = int(input('Plase enter a number to select device: [0]'))
            except:
                num = 0

        if num >= 0 and num < len(devs):
            args.port = devs[num].device
        else:
            print('Your input is incorrect!')
            exit()
    else:
        found = False
        for port in devs:
            if args.port == port.device:
                found = True
                break
        if not found:
            print('Your input is incorrect!')
            exit()

    board = Isp(args.port, args.bps)
    board.init()

    if args.info:
        board.info()

    if args.com:
        board.commandlist()

    if args.output:
        if args.len:
            args.output.write(board.readbuf(args.addr, args.len))
        else:
            print('Please spec the length of read using <-l lens>')
            exit()

    if args.input:
        board.erasemem(True)
        board.writebin(args.input.read(), args.addr)

    if args.input and args.exe:
        board.go(args.addr)


if __name__ == '__main__':
    main()
