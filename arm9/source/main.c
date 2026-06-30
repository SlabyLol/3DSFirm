#include <stdint.h>

// Hardware-Register Definitionen (3DS-spezifisch)
#define REG_PDN_CLKEN0    (*(volatile uint32_t*)0x10141000)
#define REG_ARM11_CNT     (*(volatile uint32_t*)0x10141230)
#define TOP_SCREEN_PADDR  0x18000000 // Physikalischer VRAM für den oberen Bildschirm

void delay(int count) {
    for (volatile int i = 0; i < count; i++) __asm__("nop");
}

void init_screens(void) {
    // Schalte Stromversorgung für die Display-Engine ein
    REG_PDN_CLKEN0 |= (1 << 11); 
    delay(1000);

    // Bildschirm mit einer soliden Farbe (z.B. DarkFox Blau) füllen
    uint32_t* vram = (uint32_t*)TOP_SCREEN_PADDR;
    for (int i = 0; i < (400 * 240); i++) {
        vram[i] = 0x001F3F7F; // ABGR Format
    }
}

int main(void) {
    // 1. Hardware-Infrastruktur initialisieren
    init_screens();

    // 2. ARM11 Booten vorbereiten (Resetvektoren setzen und ARM11 aufwecken)
    REG_ARM11_CNT |= 1; 

    // 3. Hauptschleife des ARM9 (System-Kontrolle & Krypto-Operationen)
    while (1) {
        // Da ARMv5 kein 'wfe' unterstützt, nutzen wir hier ein leeres Statement.
        // Der Compiler optimiert das dank der Schleifenbedingung nicht weg.
        __asm__(""); 
    }

    return 0; // Wird nie erreicht, beruhigt aber den Compiler
}
