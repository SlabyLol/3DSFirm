OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(main)

MEMORY {
    ram (rwx) : ORIGIN = 0x08000000, LENGTH = 0x10000 /* ARM9 Tightly-Coupled Memory */
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
