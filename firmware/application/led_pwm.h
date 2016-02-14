#ifndef LED_PWM_H
#define LED_PWM_H

#include <stdint.h>

typedef union {
    struct {
        uint16_t r;
        uint16_t g;
        uint16_t b;
        uint16_t w;
    };
    uint16_t arr[4];
} rgbw_t;

void pwm_init(void);

void pwm_uninit(void);

void pwm_set_value(rgbw_t *rgbw);
void pwm_get_value(rgbw_t *rgbw);

void pwm_start_fade(rgbw_t *end, uint16_t duration_ticks);
void pwm_abort_fade();

#endif
