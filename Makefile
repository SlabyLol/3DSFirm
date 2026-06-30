CC      := arm-none-eabi-gcc
OBJCOPY := arm-none-eabi-objcopy
CFLAGS  := -Wall -O2 -marm -fomit-frame-pointer -nostdlib

all: y_firm_darkfox.firm

arm9.bin: arm9/source/main.c
	$(CC) $(CFLAGS) -march=armv5te -T arm9/link.ld arm9/source/main.c -o arm9.elf
	$(OBJCOPY) -O binary arm9.elf arm9.bin

arm11.bin: arm11/source/main.c
	$(CC) $(CFLAGS) -march=armv6k -T arm11/link.ld arm11/source/main.c -o arm11.elf
	$(OBJCOPY) -O binary arm11.elf arm11.bin

y_firm_darkfox.firm: arm9.bin arm11.bin
	@echo "Generiere fehlerfreie FIRM..."
	python3 pack_firm.py arm9.bin arm11.bin y_firm_darkfox.firm

clean:
	rm -f *.elf *.bin y_firm_darkfox.firm
