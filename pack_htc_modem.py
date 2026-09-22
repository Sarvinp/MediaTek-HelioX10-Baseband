import sys
import struct
import os

def pack_modem(stock_img_path, raw_bin_path, output_img_path):
    # 1. خواندن 64 بایت اول هدر از فایل استوک
    with open(stock_img_path, 'rb') as f:
        header = bytearray(f.read(64))
    
    if len(header) < 64 or header[:4] != b'SSSS':
        print("[!] Error: Invalid stock modem header (Magic != SSSS)")
        sys.exit(1)
        
    # 2. خواندن پی‌لود خام بیلد جدید
    with open(raw_bin_path, 'rb') as f:
        payload = f.read()
    
    payload_size = len(payload)
    print(f"[*] Raw Modem Binary Size: {payload_size} bytes (0x{payload_size:08X})")
    
    # 3. به‌روزرسانی فیلد اندازه پی‌لود در آفست 0x3C (4 بایت Little Endian)
    struct.pack_into('<I', header, 0x3C, payload_size)
    
    # 4. نوشتن فایل نهایی ایمیج
    with open(output_img_path, 'wb') as f:
        f.write(header)
        f.write(payload)
        
    total_size = os.path.getsize(output_img_path)
    print(f"[+] Successfully generated: {output_img_path}")
    print(f"[+] Total Image Size: {total_size} bytes")

if __name__ == '__main__':
    stock_path = "stock_modem_1_lwg_n.img"
    raw_bin = "(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/build/LCSH6795_LWT_L/LWG/bin/LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.MOLY_LR9_W1423_MD_LWTG_MP_V24.bin"
    out_path = "modem_rebuilt_packaged.img"
    
    pack_modem(stock_path, raw_bin, out_path)
