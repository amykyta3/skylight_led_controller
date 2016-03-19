
#ifndef VEML6040_H
#define VEML6040_H

#include <stdint.h>

// Sample Integration Times
#define VEML_IT_40MS    0x00
#define VEML_IT_80MS    0x10
#define VEML_IT_160MS   0x20
#define VEML_IT_320MS   0x30
#define VEML_IT_640MS   0x40
#define VEML_IT_1280MS  0x50

typedef struct {
    uint16_t r;
    uint16_t g;
    uint16_t b;
    uint16_t w;
} veml6040_sample_t;

void veml6040_init(void);
int veml6040_start_sample(uint8_t integ_time);
void veml6040_read_result(veml6040_sample_t *result);
int veml6040_sample(uint8_t integ_time, veml6040_sample_t *result);

#endif

