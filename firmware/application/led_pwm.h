#ifndef LED_PWM_H
#define LED_PWM_H

#include <stdint.h>

void pwm_init(void);

void pwm_uninit(void);

void pwm_set_value(uint16_t red, uint16_t green, uint16_t blue, uint16_t white);

#endif
