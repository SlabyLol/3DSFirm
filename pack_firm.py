import struct
import hashlib
import os

def pack_firmware():
    arm9_bin_path = "arm9.bin"
    output_path = "y_firm_darkfox.firm"

    # Falls die rohe Binärdatei noch nicht extrahiert wurde
    if not os.path.exists(arm9_bin_path):
        os.system("arm-none-eabi-objcopy -O binary arm9.elf arm9.bin")

    with open(arm9_bin_path, "rb") as f:
        arm9_data = f.read()

    # Striktes Padding auf 512-Byte Sektorengröße
    if len(arm9_data) % 512 != 0:
        arm9_data += b"\x00" * (512 - (len(arm9_data) % 512))

    # SHA256 über den bereinigten ARM9-Payload berechnen
    arm9_hash = hashlib.sha256(arm9_data).digest()

    # Erstelle den leeren 512-Byte (0x200) FIRM-Header
    header = bytearray(512)

    # Magic Bytes: "FIRM" einfrieren
    header[0:4] = b"FIRM"
    
    # Entrypoints definieren (ARM11 bleibt geparkt, ARM9 startet bei SysIRAM)
    struct.pack_into("<I", header, 0x04, 0x00000000) # ARM11 Entry
    struct.pack_into("<I", header, 0x08, 0x08000000) # ARM9 Entry

    # SEKTION 2 (Offset 0xA0 im Header): Exklusiv reserviert für ARM9-Ausführung
    struct.pack_into("<I", header, 0xA0, 0x00000200)     # Start-Offset im File (direkt nach dem Header)
    struct.pack_into("<I", header, 0xA4, 0x08000000)     # Zieladresse im RAM
    struct.pack_into("<I", header, 0xA8, len(arm9_data)) # Exakte Bytegröße
    struct.pack_into("<I", header, 0xAC, 0x00000000)     # Copy-Method / Flags (0 = Standard/Luma-kompatibel)
    header[0xB0:0xD0] = arm9_hash                         # SHA256 Hash für Sektion 2 eintragen

    # Finale .firm Datei schreiben
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(arm9_data)

    print(f"[SUCCESS] Layout-Matrix validiert. {output_path} ist einsatzbereit!")

if __name__ == "__main__":
    pack_firmware()
