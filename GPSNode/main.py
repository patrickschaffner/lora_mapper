from network import LoRa
import socket
import binascii
import struct
import time
import pycom
from pytrack import Pytrack
from L76GNSS import L76GNSS

py = Pytrack()
gps = L76GNSS(py,timeout=5)

LORA_FREQUENCY = 868100000

# initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create OTAA authentication params (does not work with NanoGateway)
dev_eui = binascii.unhexlify('AABBCCDDEEFF2770')
app_eui = binascii.unhexlify('70B3D57ED00085DF')
app_key = binascii.unhexlify('34CFA4AECC5950D91AD5D0F77D1D82CA')

# create ABP authentication params (not recommended, but works)
dev_addr = struct.unpack(">l", binascii.unhexlify('26011F97'))[0]
nwk_session = binascii.unhexlify('F464E664666E995907F076C5ABD2765D')
app_session = binascii.unhexlify('D161A3131034B122203992D309759384')

### Hack for NanoGateway
for i in range(3, 16):
    lora.remove_channel(i)
lora.add_channel(0, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)

#lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0, dr=5)
lora.join(activation=LoRa.ABP, auth=(dev_addr,nwk_session,app_session), timeout=0, dr=5)

pycom.heartbeat(False)
pycom.rgbled(0xff0000)
print('LORA SCAN')

while not lora.has_joined():
    time.sleep(5)

conn = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
conn.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
conn.setblocking(False)

pycom.rgbled(0xbb7700)
print('LORA JOINED')

while True:

    coords = gps.coordinates()
    if coords[0] is None:
        pycom.rgbled(0xbb7700)
        continue

    pycom.rgbled(0x00ff00)
    print('GPS FIX: '+str(coords))

    msg = str(coords).encode('ascii')
    conn.send(msg)
    time.sleep(5)
    rx, port = conn.recvfrom(256)
    if rx:
        print(str(b'RECEIVED: '+rx,'ascii'))
    time.sleep(25)
