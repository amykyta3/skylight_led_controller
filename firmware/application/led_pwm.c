#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include <avr/io.h>

#include <board.h>
#include <rtc.h>
#include "led_pwm.h"

//--------------------------------------------------------------------------------------------------
typedef union {
    struct{
        uint16_t r;
        uint16_t g;
        uint16_t b;
        uint16_t w;
        uint8_t sign_r; // sign-bit
        uint8_t sign_g; 
        uint8_t sign_b; 
        uint8_t sign_w; 
    };
    struct{
        uint16_t arr[4];
        uint8_t sign[4];
    };
}delta_rgbw_t;
//--------------------------------------------------------------------------------------------------
void pwm_init(void){
    // Init TCD0
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
    TCD0.CTRLB = TC_WGMODE_SINGLESLOPE_gc | TC0_CCAEN_bm | TC0_CCBEN_bm | TC0_CCCEN_bm | TC0_CCDEN_bm;
    TCD0.CTRLD = 0x00;
    TCD0.CTRLE = TC_BYTEM_NORMAL_gc;
    
    // Set RGBW to Off
    TCD0.CCA = 0;
    TCD0.CCB = 0;
    TCD0.CCC = 0;
    TCD0.CCD = 0;
    
    // Start timer
    TCD0.CTRLA = TC_CLKSEL_DIV1_gc;
}

//--------------------------------------------------------------------------------------------------
void pwm_uninit(void){
    pwm_abort_fade();
    TCD0.CTRLA = TC_CLKSEL_OFF_gc;
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
}

//--------------------------------------------------------------------------------------------------
void pwm_set_value(rgbw_t *rgbw){
    // Write to double-buffered register so that change mid-period doesn't cause flickering
    TCD0.CCABUF = rgbw->r;
    TCD0.CCBBUF = rgbw->g;
    TCD0.CCCBUF = rgbw->b;
    TCD0.CCDBUF = rgbw->w;
}

//--------------------------------------------------------------------------------------------------
void pwm_get_value(rgbw_t *rgbw){
    rgbw->r = TCD0.CCA;
    rgbw->g = TCD0.CCB;
    rgbw->b = TCD0.CCC;
    rgbw->w = TCD0.CCD;
}

//--------------------------------------------------------------------------------------------------
#define TICKS_PER_STEP  2

static timer_t fade_timer;
static uint16_t fade_duration;
static uint16_t fade_current_tick;
static rgbw_t fade_start;
static delta_rgbw_t fade_delta;
static void fade_step_callback(void *d){
    rgbw_t rgbw;
    fade_current_tick += TICKS_PER_STEP;
    if(fade_current_tick < fade_duration){
        
        // Interpolate fade value
        for(uint8_t i=0; i<4; i++) {
            uint32_t tmp;
            tmp = fade_delta.arr[i];
            tmp *= fade_current_tick;
            tmp /= fade_duration;
            if(fade_delta.sign[i]){
                rgbw.arr[i] = fade_start.arr[i] - tmp;
            }else{
                rgbw.arr[i] = fade_start.arr[i] + tmp;
            }
        }
        pwm_set_value(&rgbw);
        
    }else{
        // finished fade. Set to end value
        for(uint8_t i=0; i<4; i++) {
            if(fade_delta.sign[i]){
                rgbw.arr[i] = fade_start.arr[i] - fade_delta.arr[i];
            }else{
                rgbw.arr[i] = fade_start.arr[i] + fade_delta.arr[i];
            }
        }
        pwm_set_value(&rgbw);
        timer_stop(&fade_timer);
        PORTA.OUTCLR = P_LED_bm;
    }
}


void pwm_start_fade(rgbw_t *end, uint16_t duration_ticks){
    struct timerctl t;
    
    pwm_get_value(&fade_start);
    for(uint8_t i=0; i<4; i++) {
        if(end->arr[i] >= fade_start.arr[i]){
            fade_delta.arr[i] = end->arr[i] - fade_start.arr[i];
            fade_delta.sign[i] = 0;
        }else{
            fade_delta.arr[i] = fade_start.arr[i] - end->arr[i];
            fade_delta.sign[i] = 1;
        }
    }
    
    fade_duration = duration_ticks;
    fade_current_tick = 0;
    
    t.interval = TICKS_PER_STEP;
    t.repeat = true;
    t.callback = fade_step_callback;
    t.callback_data = NULL;
    
    timer_start(&fade_timer, &t);
    PORTA.OUTSET = P_LED_bm;
}

void pwm_abort_fade(){
    timer_stop(&fade_timer);
}
