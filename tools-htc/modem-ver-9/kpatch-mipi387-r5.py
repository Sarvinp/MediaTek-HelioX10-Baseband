"""Round 5: silence MML1_MIPI_Gen_Data assert path for line 387.
At image offset 0x4776aa: movw r2,#0x183 (4B) + ldr r1,[pc,#0xc] (2B)
+ blx assert-veneer (4B) = 10 bytes, immediately followed by
'movs r0,#0; pop {r3,r4,r5,r6,r7,pc}'.  NOP the 10 bytes -> normal return 0.
Base: moly-nosbmipi-r4.img (EPHY 85/171/177 already neutralized).
"""
import hashlib
import struct
import sys

SRC = 'D:/htc-modem/modem-ver-9/moly-nosbmipi-r4.img'
DST = 'D:/htc-modem/modem-ver-9/moly-mipi387-r5.img'
OFF = 0x4776aa
N = 10

d = bytearray(open(SRC, 'rb').read())
orig = bytes(d[OFF:OFF+N])
if orig != bytes.fromhex('40f28312034983f79aef'):
    sys.exit('FATAL: unexpected bytes at 0x%x: %s' % (OFF, orig.hex()))
d[OFF:OFF+N] = bytes.fromhex('00bf') * (N // 2)
assert len(d) == len(open(SRC, 'rb').read())
open(DST, 'wb').write(bytes(d))
print('patched 0x%x (was %s) -> nops' % (OFF, orig.hex()))
v = open(DST, 'rb').read()
print('md5', hashlib.md5(v).hexdigest())
