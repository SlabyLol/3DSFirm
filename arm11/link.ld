OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(main)

MEMORY {
    ram (rwx) : ORIGIN = 0x1FF80000, LENGTH = 0x10000 /* Einstiegspunkt für den ARM11-Kern */
}

SECTIONS {
    .text : {
        *(.text.start)
        *(.text*)
        *(.rodata*)
    } > ram
    .data : { *(.data*) } > ram
    .bss  : { *(.bss*) } > ram
}
