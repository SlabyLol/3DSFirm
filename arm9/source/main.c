#include <stdint.h>
#include <stddef.h>

#define REG_PDN_CLKEN0    (*(volatile uint32_t*)0x10141000)
#define REG_PAD_HID       (*(volatile uint32_t*)0x10146000)
#define TOP_SCREEN_PADDR  0x18000000

// Native 3DS LCD physical orientation constants
#define SCREEN_WIDTH      240
#define SCREEN_HEIGHT     400

// Tasten-Bitmasks (Inverted raw registers)
#define BUTTON_LEFT       (1 << 5)
#define BUTTON_RIGHT      (1 << 4)

// Standard-compliant fallback memset to satisfy GCC internal compiler optimizations
void* memset(void* dest, int val, size_t count) {
    uint8_t* ptr = (uint8_t*)dest;
    while (count--) {
        *ptr++ = (uint8_t)val;
    }
    return dest;
}

// Custom 32-bit fast block memory clear to prevent CPU timing lockups
void memset32(void* dest, uint32_t val, uint32_t words) {
    uint32_t* p = (uint32_t*)dest;
    while (words--) {
        *p++ = val;
    }
}

// Simple assembly loop delay routine
void delay(int count) {
    for (volatile int i = 0; i < count; i++) {
        __asm__("nop");
    }
}

// Optimized native hardware coordinate drawing routine
void draw_rect(int x, int y, int w, int h, uint32_t color) {
    uint32_t* vram = (uint32_t*)TOP_SCREEN_PADDR;
    for (int i = 0; i < h; i++) {
        for (int j = 0; j < w; j++) {
            int px = x + j;
            int py = y + i;
            // Strict hardware boundaries check to eliminate MMIO collision crashes
            if (px >= 0 && px < SCREEN_WIDTH && py >= 0 && py < SCREEN_HEIGHT) {
                vram[py * SCREEN_WIDTH + px] = color;
            }
        }
    }
}

int main(void) {
    // 1. Force initialize display processing engine power rails
    REG_PDN_CLKEN0 |= (1 << 11); 
    delay(5000);

    // Coordinate variables bound to the native hardware landscape mapping
    int player_x = 100;
    int player_y = 350;
    int player_width = 40;
    int player_height = 10;

    int enemy_x = 110;
    int enemy_y = 40;
    int enemy_speed = 2;

    uint32_t* framebuffer = (uint32_t*)TOP_SCREEN_PADDR;
    uint32_t total_pixels = SCREEN_WIDTH * SCREEN_HEIGHT;

    // 2. Hardware Main Executive Loop
    while (1) {
        // FAST BLOCK CLEAR: Eliminates execution lag completely
        memset32(framebuffer, 0x00000000, total_pixels);

        // Read raw button inputs (Bitwise NOT because active-low hardware registers)
        uint32_t kDown = ~REG_PAD_HID;

        if (kDown & BUTTON_LEFT)  player_x -= 4;
        if (kDown & BUTTON_RIGHT) player_x += 4;

        // Keep player strictly bound inside the physical LCD matrix boundary
        if (player_x < 0) player_x = 0;
        if (player_x > SCREEN_WIDTH - player_width) player_x = SCREEN_WIDTH - player_width;

        // Basic automated enemy path logic
        enemy_x += enemy_speed;
        if (enemy_x <= 0 || enemy_x >= SCREEN_WIDTH - 20) {
            enemy_speed = -enemy_speed;
        }

        // Render entities via direct safe writes
        // Player Entity (DarkFox Blue)
        draw_rect(player_x, player_y, player_width, player_height, 0x001F3F7F);
        // Enemy Entity (Red Asteroid)
        draw_rect(enemy_x, enemy_y, 20, 20, 0x000000FF);

        // Frame pacing delay logic
        delay(40000);
    }

    return 0;
}
