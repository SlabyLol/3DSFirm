import sys
import struct
import hashlib

def get_sha256(data):
    return hashlib.sha256(data).digest()

def make_firm(arm9_path, arm11_path, out_path):
    with open(arm9_path, "rb") as f: arm9_data = f.read()
    with open(arm11_path, "rb") as f: arm11_data = f.read()

    # Padding für ARM11 berechnen (Größe muss an 0x200 Byte Blöcken ausgerichtet sein)
    arm11_padded_len = (len(arm11_data) + 0x1FF) & ~0x1FF
    arm11_padding = b"\x00" * (arm11_padded_len - len(arm11_data))
    arm11_total_data = arm11_data + arm11_padding

    # Hashes der Sektionen generieren
    arm11_hash = get_sha256(arm11_total_data)
    arm9_hash = get_sha256(arm9_data)

    # FIRM-Magic ("FIRM")
    header = bytearray(b"FIRM")
    header += struct.pack("<I", 0) # Priority
    header += struct.pack("<I", 0x08000000) # ARM9 Entry Point
    header += struct.pack("<I", 0x1FF80000) # ARM11 Entry Point
    header += b"\x00" * 0x30 # Reserved

    # Sektion 0: ARM11
    header += struct.pack("<I", 0x200) # Offset im File
    header += struct.pack("<I", 0x1FF80000) # Native Ziel-Adresse im RAM
    header += struct.pack("<I", len(arm11_total_data)) # Größe im File
    header += struct.pack("<I", 0) # Typ 0: ARM11
    header += arm11_hash # Der berechnete SHA256 Hash!

    # Sektion 1: ARM9
    arm9_offset = 0x200 + arm11_padded_len
    header += struct.pack("<I", arm9_offset)
    header += struct.pack("<I", 0x08000000) # Native Ziel-Adresse im RAM
    header += struct.pack("<I", len(arm9_data)) # Größe im File
    header += struct.pack("<I", 1) # Typ 1: ARM9
    header += arm9_hash # Der berechnete SHA256 Hash!

    # Die restlichen beiden Sektionen (2 und 3) bleiben ungenutzt
    header += b"\x00" * (0x30 * 2)

    # Header auf exakt 0x200 Bytes auffüllen
    header += b"\x00" * (0x200 - len(header))

    # Finale .firm Datei schreiben
    with open(out_path, "wb") as f:
        f.write(header)
        f.write(arm11_total_data)
        f.write(arm9_data)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python firm_tool.py <arm9.bin> <arm11.bin> <output.firm>")
    else:
        make_firm(sys.argv[1], sys.argv[2], sys.argv[3])
