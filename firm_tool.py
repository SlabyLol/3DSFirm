import sys
import struct

def make_firm(arm9_path, arm11_path, out_path):
    with open(arm9_path, "rb") as f: arm9_data = f.read()
    with open(arm11_path, "rb") as f: arm11_data = f.read()

    # FIRM-Magic ("FIRM")
    header = bytearray(b"FIRM")
    header += struct.pack("<I", 0) # Priority
    header += struct.pack("<I", 0x08000000) # ARM9 Entry Point
    header += struct.pack("<I", 0x1FF80000) # ARM11 Entry Point
    header += b"\x00" * 0x30 # Reserved / Padding

    # Sektion 0: ARM11
    header += struct.pack("<I", 0x200) # Offset im File
    header += struct.pack("<I", 0x1FF80000) # Native Adresse
    header += struct.pack("<I", len(arm11_data)) # Größe
    header += struct.pack("<I", 0) # Type (ARM11)
    header += b"\x00" * 32 # SHA256 Platzhalter

    # Sektion 1: ARM9
    arm9_offset = 0x200 + ((len(arm11_data) + 0x1FF) & ~0x1FF)
    header += struct.pack("<I", arm9_offset)
    header += struct.pack("<I", 0x08000000)
    header += struct.pack("<I", len(arm9_data))
    header += struct.pack("<I", 1) # Type (ARM9)
    header += b"\x00" * 32 # SHA256 Platzhalter

    # Restliche Sektionen leeren (Insgesamt 4 Sektionen im Header)
    header += b"\x00" * (0x30 * 2)
    header += b"\x00" * (0x200 - len(header)) # Header auf 0x200 Bytes auffüllen

    # Zusammenfügen
    with open(out_path, "wb") as f:
        f.write(header)
        f.write(arm11_data)
        # Alignment padding
        f.write(b"\x00" * (((0x200 - len(arm11_data)) % 0x200)))
        f.write(arm9_data)

if __name__ == "__main__":
    make_firm(sys.argv[1], sys.argv[2], sys.argv[3])
