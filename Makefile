# --- DarkFox Co. Hardware Compilation Matrix ---

# Compiler- und Toolchain-Definitionen
CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
RM      := rm -f

# Verzeichnis-Strukturen
SOURCE  := arm9/source/main.c
LINKER  := arm9/link.ld
ELF     := arm9.elf
BIN     := arm9.bin
TARGET  := y_firm_darkfox.firm

# Compiler-Flags für das nackte Bare-Metal-System
CFLAGS  := -Wall -O2 -marm -fomit-frame-pointer -nostdlib -march=armv5te -T $(LINKER)

# Standard-Target: Führt die gesamte Kette aus
all: $(TARGET)

$(TARGET): $(SOURCE)
	@echo "1/4 -> Säubere alte Build-Fragmente..."
	@$(RM) $(ELF) $(BIN) $(TARGET)
	
	@echo "2/4 -> Kompiliere optimierten ARM9-C-Code..."
	$(CC) $(CFLAGS) $(SOURCE) -o $(ELF)
	
	@echo "3/4 -> Extrahiere flache Hardware-Binärdatei..."
	$(OBJCOPY) -O binary $(ELF) $(BIN)
	
	@echo "4/4 -> Verpacke verschlüsselte NDMA-Strukturen via firmtool..."
	firmtool build $(TARGET) -e 0x08000000 -D $(BIN) -A 0x08000000 -C NDMA
	@echo "[SUCCESS] $(TARGET) wurde erfolgreich für die Hardware kalibriert!"

# Bereinigungs-Target für den Workspace
clean:
	@echo "Bereinige Workspace..."
	@$(RM) $(ELF) $(BIN) $(TARGET)

.PHONY: all clean
