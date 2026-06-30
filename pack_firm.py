import struct
import hashlib
import os

def pack_firmware():
    arm9_bin_path = "arm9.bin"
    output_path = "y_firm_darkfox.firm"

    if not os.path.exists(arm9_bin_path):
        # Fallback if you haven't extracted raw binary from elf yet
        os.system("arm-none-eabi-objcopy -O binary arm9.elf arm9.bin")

    with open(arm9_bin_path, "rb") as f:
        arm9_data = f.read()

    # Pad ARM9 data to a perfect 512-byte sector boundary
    if len(arm9_data) % 512 != 0:
        arm9_data += b"\x00" * (512 - (len(arm9_data) % 512))

    # Calculate SHA256 checksum of the padded payload segment
    arm9_hash = hashlib.sha256(arm9_data).digest()

    # Generate the 512-byte (0x200) standard FIRM Header Layout
    header = bytearray(512)

    # Magic Bytes: 'FIRM'
    header[0:4] = b"FIRM"
    
    # Target execution priorities (ARM11 disabled / ARM9 primary entry)
    struct.pack_into("<I", header, 0x04, 0x00000000) # ARM11 Entry Address (None)
    struct.pack_into("<I", header, 0x08, 0x08000000) # ARM9 Entry Address (SysIRAM)

    # Section 0: Setup ARM9 Header Entries
    struct.pack_into("<I", header, 0x40, 0x00000200) # File offset where payload starts
    struct.pack_into("<I", header, 0x44, 0x08000000) # Native Target Memory Destination
    struct.pack_into("<I", header, 0x48, len(arm9_data)) # Size of the sector allocation
    struct.pack_into("<I", header, 0x4C, 0x00000001) # Core assignment tag (ARM9 block)
    header[0x50:0x70] = arm9_hash                     # Store calculated block checksum

    # Write out the final configured bare-metal image
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(arm9_data)

    print(f"SUCCESS: {output_path} generated and packed successfully.")

if __name__ == "__main__":
    pack_firmware()
