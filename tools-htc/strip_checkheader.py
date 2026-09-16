#!/usr/bin/env python3
'''Round 1 of MD-no-boot hunt: build a legacy (CheckHeader-less) MOLY image.

Why: HTC mdinit takes a different driver path for images WITHOUT the
trailing 284B V3 CheckHeader (stock: header size -1, MD image check 188).
Our MOLY build appends it via tools/append2.pl and then hangs pre-clock with
md size sync warning (03f00000 vs 08000000). Stripping forces our image down
the same driver path as working stock.
Usage: strip_checkheader.py <new_bin> <header_template_img> <out_img>
'''
import struct
import sys
STRUCT = 284
def main(bin_path, hdr_img_path, out_path):
    raw = open(bin_path, 'rb').read()
    assert raw[-STRUCT:-STRUCT + 12] == b'CHECK_HEADER', 'no CHECK_HEADER tail'
    assert struct.unpack('<I', raw[-4:])[0] == STRUCT, 'bad struct size'
    payload = raw[:-STRUCT]
    hdr = bytearray(open(hdr_img_path, 'rb').read()[:300])
    assert hdr[:4] == b'SSSS', 'bad SSSS header'
    hdr[60:64] = struct.pack('<I', len(payload))
    open(out_path, 'wb').write(bytes(hdr) + payload)
    print('stripped %d -> payload %d, img %d' % (len(raw), len(payload), len(payload) + 300))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
