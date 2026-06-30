#include <stdint.h>

#define REG_PDN_CLKEN0    (*(volatile uint32_t*)0x10141000)
#define REG_PAD_HID       (*(volatile uint32_t*)0x10146000) // Tasten-Register
#define TOP_SCREEN_PADDR  0x18000000

// Tasten-Bitmasks der 3DS
#define BUTTON_LEFT   (1 << 5)
#define BUTTON_RIGHT  (1 << 4)
#define BUTTON_A      (1 << 0)

// Spielfeld-Größe (3DS Top Screen: 400x240)
#define SCREEN_WIDTH  400
#define SCREEN_HEIGHT 240

// Eigene memset-Implementierung mit uint32_t für maximale Unabhängigkeit von Headern
void* memset(void* dest, int c, uint32_t n) {
    uint8_t* p = dest;
    while (n--) {
        *p++ = (uint8_t)c;
    }
    return dest;
}

void delay(int count) {
    for (volatile int i = 0; i < count; i++) __asm__("nop");
}

// Zeichnet ein ausgefülltes Rechteck (für Spieler und Gegner)
void draw_rect(int x, int y, int w, int h, uint32_t color) {
    uint32_t* vram = (uint32_t*)TOP_SCREEN_PADDR;
    for (int i = 0; i < h; i++) {
        for (int j = 0; j < w; j++) {
            int py = y + i;
            int px = x + j;
            if (px >= 0 && px < SCREEN_WIDTH && py >= 0 && py < SCREEN_HEIGHT) {
                vram[py * SCREEN_WIDTH + px] = color;
            }
        }
    }
}

int main(void) {
    // Bildschirm-Hardware aktivieren
    REG_PDN_CLKEN0 |= (1 << 11); 
    delay(1000);

    // Spiel-Variablen
    int player_x = 180;
    int player_y = 200;
    int player_width = 40;
    int player_height = 10;

    int enemy_x = 200;
    int enemy_y = 20;
    int enemy_speed = 2;

    // Hauptspielschleife (Bare-Metal Game Loop)
    while (1) {
        // 1. Alten Zustand löschen (Bildschirm schwarz färben)
        draw_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0x00000000);

        // 2. Input abfragen (Register invertieren, da 0 = gedrückt)
        uint32_t kDown = ~REG_PAD_HID;

        if (kDown & BUTTON_LEFT)  player_x -= 4;
        if (kDown & BUTTON_RIGHT) player_x += 4;

        // Grenzen einhalten
        if (player_x < 0) player_x = 0;
        if (player_x > SCREEN_WIDTH - player_width) player_x = SCREEN_WIDTH - player_width;

        // 3. Gegner-Logik (KI bewegt sich hin und her)
        enemy_x += enemy_speed;
        if (enemy_x <= 0 || enemy_x >= SCREEN_WIDTH - 20) {
            enemy_speed = -enemy_speed; // Richtung wechseln
        }

        // 4. Objekte zeichnen
        // Spieler (DarkFox Blau)
        draw_rect(player_x, player_y, player_width, player_height, 0x001F3F7F);
        // Gegner / Asteroid (Rot)
        draw_rect(enemy_x, enemy_y, 20, 20, 0x000000FF);

        // 5. Frame-Rate stabilisieren (Simples V-Sync Delay)
        delay(50000);
    }

    return 0;
}
