import struct
import serial
from serial import SerialException
from serial.tools import list_ports
import numpy as np
from PIL import Image
import threading
lock = threading.Lock()

# USB Debug commands
USBDBG_CMD              = 48
USBDBG_FW_VERSION       = 0x80
USBDBG_FRAME_SIZE       = 0x81
USBDBG_FRAME_DUMP       = 0x82
USBDBG_ARCH_STR         = 0x83
USBDBG_SCRIPT_EXEC      = 0x05
USBDBG_SCRIPT_STOP      = 0x06
USBDBG_SCRIPT_SAVE      = 0x07
USBDBG_SCRIPT_RUNNING   = 0x87
USBDBG_TEMPLATE_SAVE    = 0x08
USBDBG_DESCRIPTOR_SAVE  = 0x09
USBDBG_ATTR_READ        = 0x8A
USBDBG_ATTR_WRITE       = 0x0B
USBDBG_SYS_RESET        = 0x0C
USBDBG_FB_ENABLE        = 0x0D
USBDBG_TX_BUF_LEN       = 0x8E
USBDBG_TX_BUF           = 0x8F

ATTR_CONTRAST           = 0
ATTR_BRIGHTNESS         = 1
ATTR_SATURATION         = 2
ATTR_GAINCEILING        = 3

BOOTLDR_START           = 0xABCD0001
BOOTLDR_RESET           = 0xABCD0002
BOOTLDR_ERASE           = 0xABCD0004
BOOTLDR_WRITE           = 0xABCD0008
BOOTLDR_FLASH           = 0xABCD0010


def get_openmv_port():
    for port in list_ports.comports():
        if 'OpenMV' in port.description:
            return port.device
    return None


def lock_func(func):
    def decorator(*args, **kwargs):
        with lock:
            result = func(*args, **kwargs)
        return result
    return decorator


class OpenMV(object):
    def __init__(self, *args):
        self._serial = None
        self._fw_version = None
        self._connect = False
        self._port = get_openmv_port()
        super(OpenMV, self).__init__(*args)

    def __del__(self):
        if self._serial:
            self._serial.close()

    @lock_func
    def connect(self):
        if not self._connect:
            if self._port:
                try:
                    self._serial = serial.Serial(self._port, baudrate=921600, timeout=0.3)
                    self._connect = True
                except SerialException as e:
                    print(e)
        return self._connect

    @property
    def port(self):
        return self._port

    @lock_func
    def disconnect(self):
        if self._serial:
            try:
                self._serial.close()
                self._serial = None
            except:
                pass

    @property
    def fw_version(self):
        if not self._fw_version:
            self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FW_VERSION, 12))
            ver = struct.unpack("<3I", self._serial.read(12))
            self._fw_version = '{}.{}.{}'.format(*ver)

        return self._fw_version

    @property
    def fb_size(self):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FRAME_SIZE, 12))
        return struct.unpack("<3I", self._serial.read(12))

    @lock_func
    def exec_script(self, buf):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_EXEC, len(buf)))
        self._serial.write(buf.encode())

    @lock_func
    def stop_script(self):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_STOP, 0))

    def fb_enable(self, enable):
        self._serial.write(struct.pack("<BBIH", USBDBG_CMD, USBDBG_FB_ENABLE, 0, enable))

    @lock_func
    def fb_dump(self):
        size = self.fb_size

        if not size[0]:
            # frame not ready
            return None

        if size[2] > 2:  # JPEG
            num_bytes = size[2]
        else:
            num_bytes = size[0]*size[1]*size[2]

        # read fb data
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FRAME_DUMP, num_bytes))
        buff = self._serial.read(num_bytes)

        if size[2] == 1:  # Grayscale
            y = np.fromstring(buff, dtype=np.uint8)
            buff = np.column_stack((y, y, y))
        elif size[2] == 2:  # RGB565
            arr = np.fromstring(buff, dtype=np.uint16).newbyteorder('S')
            r = (((arr & 0xF800) >> 11)*255.0/31.0).astype(np.uint8)
            g = (((arr & 0x07E0) >> 5) * 255.0/63.0).astype(np.uint8)
            b = (((arr & 0x001F) >> 0) * 255.0/31.0).astype(np.uint8)
            buff = np.column_stack((r, g, b))
        else:  # JPEG
            try:
                buff = np.asarray(Image.frombuffer("RGB", size[0:2], buff, "jpeg", "RGB", ""))
            except Exception as e:
                print("JPEG decode error (%s)" % (e))
                return None

        if (buff.size != (size[0]*size[1]*3)):
            return None

        return (size[0], size[1], buff.reshape((size[1], size[0], 3)))

    @property
    def arch_id(self):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_ARCH_STR, 64))
        return self._serial.read(64).split(b'\x00', 1)[0].decode()

    def reset(self):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SYS_RESET, 0))

    @lock_func
    def bootloader_start(self):
        try:
            self._serial.write(struct.pack("<I", BOOTLDR_START))
            boot_magic = struct.unpack("I", self._serial.read(4))[0]
            if boot_magic != BOOTLDR_RESET:
                print('error boot magic:', hex(boot_magic))
                return False
            else:
                return True
        except:
            return False

    @lock_func
    def bootloader_reset(self):
        self._serial.write(struct.pack("<I", BOOTLDR_RESET))

    @lock_func
    def bootloader_flash(self):
        self._serial.write(struct.pack("<I", BOOTLDR_FLASH))
        return struct.unpack("3I", self._serial.read(12))

    @lock_func
    def flash_erase(self, sector):
        self._serial.write(struct.pack("<II", BOOTLDR_ERASE, sector))

    @lock_func
    def flash_write(self, buf):
        self._serial.write(struct.pack("<I", BOOTLDR_WRITE) + buf)

    @lock_func
    def tx_buf_len(self):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_TX_BUF_LEN, 4))
        return struct.unpack("I", self._serial.read(4))[0]

    @lock_func
    def tx_buf(self, bytes):
        self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_TX_BUF, bytes))
        return self._serial.read(bytes)
