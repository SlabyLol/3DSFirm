#include <stdint.h>

void __attribute__((noreturn)) main(void) {
    // Der ARM11 wird vom ARM9 geweckt.
    // Hier wird das Patching des originalen 3DS-Kernels (Firm Launch) vorbereitet.
    
    while (1) {
        // Deine Logik für Homebrew-Enabler, Debugger oder Overclocking
        __asm__("wfi");
    }
}
