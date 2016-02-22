#include <stdint.h>
#include <stddef.h>
#include <board.h>
#include <rtc.h>

#include "led_pwm.h"
#include "led_transitions.h"
#include "eeprom_config.h"

//==============================================================================
// Internal
//==============================================================================
#define TICKS_PER_STEP  2

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

static struct{
    transition_t *current_transition;
    timer_t timer;
    struct{
        uint16_t duration;
        uint16_t current_tick;
        rgbw_t start;
        delta_rgbw_t delta;
        void (*callback)(void);
    }fade;
} context;

//------------------------------------------------------------------------------
static void fade_step_callback(void *d){
    rgbw_t rgbw;
    context.fade.current_tick += TICKS_PER_STEP;
    if(context.fade.current_tick < context.fade.duration){
        
        // Interpolate fade value
        for(uint8_t i=0; i<4; i++) {
            uint32_t tmp;
            tmp = context.fade.delta.arr[i];
            tmp *= context.fade.current_tick;
            tmp /= context.fade.duration;
            if(context.fade.delta.sign[i]){
                rgbw.arr[i] = context.fade.start.arr[i] - tmp;
            }else{
                rgbw.arr[i] = context.fade.start.arr[i] + tmp;
            }
        }
        pwm_set_value(&rgbw);
        
    }else{
        // finished fade. Set to end value
        for(uint8_t i=0; i<4; i++) {
            if(context.fade.delta.sign[i]){
                rgbw.arr[i] = context.fade.start.arr[i] - context.fade.delta.arr[i];
            }else{
                rgbw.arr[i] = context.fade.start.arr[i] + context.fade.delta.arr[i];
            }
        }
        pwm_set_value(&rgbw);
        timer_stop(&context.timer);
        if(context.fade.callback){
            context.fade.callback();
        }
    }
}

//------------------------------------------------------------------------------
static void fade_start(rgbw_t *end, uint16_t duration_ticks, void (*callback)(void)){
    struct timerctl t;
    
    pwm_get_value(&context.fade.start);
    for(uint8_t i=0; i<4; i++) {
        if(end->arr[i] >= context.fade.start.arr[i]){
            context.fade.delta.arr[i] = end->arr[i] - context.fade.start.arr[i];
            context.fade.delta.sign[i] = 0;
        }else{
            context.fade.delta.arr[i] = context.fade.start.arr[i] - end->arr[i];
            context.fade.delta.sign[i] = 1;
        }
    }
    
    context.fade.duration = duration_ticks;
    context.fade.current_tick = 0;
    context.fade.callback = callback;
    
    t.interval = TICKS_PER_STEP;
    t.repeat = true;
    t.callback = fade_step_callback;
    t.callback_data = NULL;
    
    timer_start(&context.timer, &t);
}

//------------------------------------------------------------------------------
static void cb_transition_done(void);
///\brief Callback. Executed after initial transition delay
static void cb_transition_post_delay(void *unused){
    switch(context.current_transition->type){
        case TRANS_IMMEDIATE:
            pwm_set_value(&context.current_transition->immediate.color);
            cb_transition_done();
            break;
            
        case TRANS_FADE:
            fade_start(&context.current_transition->fade.color,
                        context.current_transition->fade.duration,
                        cb_transition_done);
            break;
            
        case TRANS_WAVEFORM:
            #warning "TODO: Write this"
            cb_transition_done();
            break;
            
        default:
            // Undefined transition. End.
            cb_transition_done();
            break;
    }
}
//------------------------------------------------------------------------------
///\brief Callback. Executed once transition has been completed
static void cb_transition_done(void){
    context.current_transition = NULL;
}

//==============================================================================
// Public Functions
//==============================================================================
void transition_init(void){
    context.current_transition = NULL;
}

//------------------------------------------------------------------------------
void transition_start(transition_t *transition){
    transition_abort();
    
    context.current_transition = transition;
    if(transition->delay){
        // Insert a delay before executing the transition
        struct timerctl t;
        t.interval = transition->delay;
        t.repeat = false;
        t.callback = cb_transition_post_delay;
        t.callback_data = NULL;
        timer_start(&context.timer, &t);
    }else{
        cb_transition_post_delay(NULL);
    }
}

//------------------------------------------------------------------------------
void transition_abort(void){
    timer_stop(&context.timer);
    context.current_transition = NULL;
}
