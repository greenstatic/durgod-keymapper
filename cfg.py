#!/usr/bin/env python3

import sys
import hid # pip install hidapi
from struct import pack, unpack

VENDOR_ID = 0x2f68 
PRODUCT_ID = 0x0082 # DURGOD Taurus K320:
TIMEOUT = 200

KEEPALIVE   = b"\x00\x03\x07\xE3"
RESET       = b"\x00\x03\x05\x80\x04\xff".ljust(64, b"\x00")
WRITE       = b"\x00\x03\x05\x81\x0f\x00\x00"
SAVE        = b"\x00\x03\x05\x82"
DISCONNECT  = b"\x00\x03\x19\x88" # Disconnect? is sent on application exit 

keymap = [
b"\x00\x00\x00\x29\x00\x00\x00\x89\x00\x00\x00\x3a\x00\x00\x00\x3b\x00\x00\x00\x3c\x00\x00\x00\x3d\x00\x00\x00\x3e\x00\x00\x00\x3f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x40\x00\x00\x00\x41\x00\x00\x00\x42\x00\x00\x00\x43\x00\x00\x00\x44\x00\x00\x00\x45\x00\x00\x00\x46\x00\x00\x00\x47\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x35\x00\x00\x00\x1e\x00\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x20\x00\x00\x00\x21\x00\x00\x00\x22\x00\x00\x00\x23\x00\x00\x00\x24\x00\x00\x00\x25\x00\x00\x00\x26\x00\x00\x00\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x2d\x00\x00\x00\x2e\x00\x00\x00\x2a\x00\x00\x00\x49\x00\x00\x00\x4a\x00\x00\x00\x4b\x00\x00\x00\x53\x00\x00\x00\x54\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x55\x00\x00\x00\x56\x00\x00\x00\x2b\x00\x00\x00\x14\x00\x00\x00\x1a\x00\x00\x00\x08\x00\x00\x00\x15\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x1c\x00\x00\x00\x18\x00\x00\x00\x0c\x00\x00\x00\x12\x00\x00\x00\x13\x00\x00\x00\x2f\x00\x00\x00\x30\x00\x00\x00\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x4c\x00\x00\x00\x4d\x00\x00\x00\x4e\x00\x00\x00\x5f\x00\x00\x00\x60\x00\x00\x00\x61\x00\x00\x00\x57\x00\x00\x00\x39\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",

b"\x00\x00\x00\x04\x00\x00\x00\x16\x00\x00\x00\x07\x00\x00\x00\x09\x00\x00\x00\x0a\x00\x00\x00\x0b\x00\x00\x00\x0d\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x0f\x00\x00\x00\x33\x00\x00\x00\x34\x00\x00\x00\x32\x00\x00\x00\x28\x00\x00\x00\x4c\x00\x00\x00\x4d\x00\x00\x00\x4e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x5c\x00\x00\x00\x5d\x00\x00\x00\x5e\x00\x00\x00\x85\x00\x00\x00\xe1\x00\x00\x00\x64\x00\x00\x00\x1d\x00\x00\x00\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x06\x00\x00\x00\x19\x00\x00\x00\x05\x00\x00\x00\x11\x00\x00\x00\x10\x00\x00\x00\x36\x00\x00\x00\x37\x00\x00\x00\x38\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x87\x00\x00\x00\xe5\x00\x00\x00\x00\x00\x00\x00\x52\x00\x00\x00\x00\x00\x00\x00\x59\x00\x00\x00\x5a\x00\x00\x00\x5b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x00\xe3\x00\x00\x00\xe2\x00\x00\x00\x8b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x00\x00\x00\x00\x8a\x00\x00\x00\x88\x00\x00\x00\xe6\x00\x01\x00\x00\x00\x00\x00\xe7\x00\x00\x00\xe4\x00\x00\x00\x50\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
b"\x00\x00\x00\x51\x00\x00\x00\x4f\x00\x00\x00\x00\x00\x00\x00\x62\x00\x00\x00\x63\x00\x00\x00\x58\x00\x00\x00\x00\x00\x78\x56\x34\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
]

KEYNAMES = dict()
KEYNAMES[0x28] = 'Enter'
KEYNAMES[0x2C] = 'Space'
KEYNAMES[0x49] = 'Insert'
KEYNAMES[0xE0] = 'LCtrl'
KEYNAMES[0xE1] = 'LShift'
KEYNAMES[0xE2] = 'LAlt'
KEYNAMES[0xE3] = 'LWindows'
KEYNAMES[0xE4] = 'RCtrl'
KEYNAMES[0xE5] = 'RShift'
KEYNAMES[0xE6] = 'RAlt'
KEYNAMES[0xE7] = 'RWindows'

KEYNAMES[0x2B] = 'Tab'
KEYNAMES[0x39] = 'CapsLock'

KEYNAMES[0x2a] = 'Backspace'
KEYNAMES[0x4a] = 'Pos1'
KEYNAMES[0x4b] = 'PageUp'
KEYNAMES[0x4c] = 'Delete'
KEYNAMES[0x4d] = 'End'
KEYNAMES[0x4e] = 'PageDown'
KEYNAMES[0x50] = 'Left'
KEYNAMES[0x51] = 'Down'
KEYNAMES[0x52] = 'Up'
KEYNAMES[0x4f] = 'Right'
KEYNAMES[0x46] = 'Print'
KEYNAMES[0x47] = 'Roll'
KEYNAMES[0x48] = 'Roll'



def stripnulls(resp):

    l = None
    for i in range(len(resp), 0):
        if resp[i] != b'\x00':
            print("break", i)
            l=i
            break

    return resp[0:l]


def send(device, data):
    if device.write(data.ljust(64, b"\x00")) < 0: 
        raise "Write failed"

    resp = device.read(64, timeout_ms=500)
    print("<-", end="")
    print(bytearray(resp).rstrip(b'\x00'))




def reprogram():
    device_info = next(device for device in hid.enumerate() if device['vendor_id'] == VENDOR_ID and device['product_id'] == PRODUCT_ID and device['interface_number'] == 2 )

    device = hid.device()
    device.open_path(device_info['path'])

    send(device, KEEPALIVE)
    send(device, RESET)

    for i, d in enumerate(keymap):
        send(device, b''.join([WRITE, pack('b', i), d]))

    send(device, SAVE)
    send(device, KEEPALIVE)
    send(device, DISCONNECT) 
    device.close()



if __name__ == '__main__':
    N = 8
    ROW_LENGTH = 21

    keymap_parsed = []
    for d in keymap:
        row = d[0:N*4]
        keymap_parsed += unpack('>'  + N*'I', row)

    for i, c in enumerate(keymap_parsed):
        if (i % ROW_LENGTH) == 0:
            print("")
        if c in KEYNAMES:
            print("%10s" % KEYNAMES[c], end='\t')
        elif c>=0x1E and c<0x1E+9:
            # 1-9
            print("         %s" % (1+c-0x1e), end='\t')
        elif c>=0x3A and c<0x3A+12:
            # f1-f12
            keyname = 'f%s' % (1+c-0x3A)
            print("%10s" % keyname, end='\t')
        elif c>=4 and c<(26+4):
            # a-z
            print("%10s" % chr(ord('a')+c-4), end='\t')
        else:
            print("%9xh" % c, end='\t')

        #TODO: 12000000
    print("")

    #reprogram()

