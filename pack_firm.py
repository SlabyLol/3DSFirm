import sys
import struct
import hashlib

def sha256(data):
    return hashlib.sha256(data).digest()

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 pack_firm.py <arm9.bin> <arm11.bin> <output.firm>")
        return

    with open(sys.argv[1], "rb") as f: arm9 = f.read()
    with open(sys.argv[2], "rb") as f: arm11 = f.read()

    # 1. Padding auf 0x200 Byte Blöcke (Vorschrift für 3DS-NAND/SD)
    arm11_padded = arm11 + b"\x00" * ((0x200 - (len(arm11) % 0x200)) % 0x200)
    arm9_padded = arm9 + b"\x00" * ((0x200 - (len(arm9) % 0x200)) % 0x200)

    # 2. FIRM Header aufbauen (0x200 Bytes)
    header = bytearray(0x200)
    
    # Magic & Entry Points
    struct.pack_into("<4s", header, 0, b"FIRM")
    struct.pack_into("<I", header, 4, 0)          # Priority
    struct.pack_into("<I", header, 8, 0x1FF80000) # ARM11 Entry
    struct.pack_into("<I", header, 12, 0x08000000) # ARM9 Entry

    # Sektion 0: ARM11
    offset_arm11 = 0x200
    struct.pack_into("<I", header, 0x40, offset_arm11)
    struct.pack_into("<I", header, 0x44, 0x1FF80000)
    struct.pack_into("<I", header, 0x48, len(arm11_padded))
    struct.pack_into("<I", header, 0x4C, 0) # Typ 0 (ARM11)
    header[0x50:0x70] = sha256(arm11_padded)

    # Sektion 1: ARM9
    offset_arm9 = offset_arm11 + len(arm11_padded)
    struct.pack_into("<I", header, 0x70, offset_arm9)
    struct.pack_into("<I", header, 0x74, 0x08000000)
    struct.pack_into("<I", header, 0x78, len(arm9_padded))
    struct.pack_into("<I", header, 0x7C, 1) # Typ 1 (ARM9)
    header[0x80:0xA0] = sha256(arm9_padded)

    # 3. Dummy RSA-2048 Signatur am Ende des Headers (0x100 Bytes ab Offset 0x100)
    # Das füllt die Krypto-Validierung aus, damit kein Checksum/Signature-Fail kommt
    header[0x100:0x200] = b"\x00" * 0x100 

    # Schreiben
    with open(sys.argv[3], "wb") as f:
        f.write(header)
        f.write(arm11_padded)
        f.write(arm9_padded)

if __name__ == "__main__":
    main()
