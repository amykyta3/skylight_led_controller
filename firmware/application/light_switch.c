
#include <stdint.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <event_queue.h>

#include <board.h>
#include "eeprom_config.h"
#include "led_pwm.h"
#include "led_transitions.h"
#include "debug.h"


#define F_CPU   (32000000UL)

#define TIMER_PRESCALE  1024
#define TIMER_PRESCALE_gc  TC_CLKSEL_DIV1024_gc

#define TIMER_MS2TICKS(ms) (((ms)*(F_CPU/TIMER_PRESCALE))/1000)
//--------------------------------------------------------------------------------------------------

static uint8_t edge_counter;

//--------------------------------------------------------------------------------------------------
void light_switch_init(){
    
    edge_counter = 0;
    
    // Pre-configure timer
    TCE0.CTRLA = TC_CLKSEL_OFF_gc;
    TCE0.CTRLFSET = TC_CMD_RESET_gc;
    TCE0.INTFLAGS = TC0_CCAIF_bm | TC0_CCBIF_bm;
    TCE0.INTCTRLB = TC_CCAINTLVL_MED_gc | TC_CCBINTLVL_MED_gc;
    TCE0.CCA = TIMER_MS2TICKS(50);  // Debounce period
    TCE0.CCB = TIMER_MS2TICKS(500); // Event-done timeout
    
    // Set up interrupt on pin to whatever is opposite of the current state
    // Level-sensitive interrupt only exists for 0 state.
    // Invert pin as appropriate;
    PORTA.PIN4CTRL = 0;
    if((PORTA.IN & P_PWR_SENSE_bm) == 0){
        PORTA.PIN4CTRL = PORT_INVEN_bm;
    }
    
    // Enable pin interrupt ID 1 (uart flow control is already using 0)
    PORTA.INTFLAGS = PORT_INT1IF_bm;
    PORTA.INTCTRL &= ~PORT_INT1LVL_gm;
    PORTA.INT1MASK = P_PWR_SENSE_bm;
    PORTA.PIN4CTRL |= PORT_ISC_LEVEL_gc;
    PORTA.INTCTRL |= PORT_INT1LVL_MED_gc;
}

//--------------------------------------------------------------------------------------------------
ISR(PORTA_INT1_vect){
    // Pin transition detected.
    
    // Disable pin interrupt
    PORTA.INT1MASK = 0;
    PORTA.INTFLAGS = PORT_INT1IF_bm;
    
    // Start debounce timer
    TCE0.CTRLFSET = TC_CMD_RESTART_gc;
    TCE0.CTRLA = TC_CLKSEL_DIV1024_gc;
}

//--------------------------------------------------------------------------------------------------
ISR(TCE0_CCA_vect){
    // Pin debounce period expired.
    // Check if pin is still in the same state
    if(PORTA.IN & P_PWR_SENSE_bm){
        // Pin already returned to original state. False alarm. 
        
        // Stop timer
        TCE0.CTRLA = TC_CLKSEL_OFF_gc;
        
    } else {
        // Detected a successful edge.
        if((PORTA.PIN4CTRL & PORT_INVEN_bm) == 0){
            // pin transitioned from 1-->0, AKA light switch off-->on
            edge_counter++;
        }
        
        // Flip pin sensitivity
        PORTA.PIN4CTRL ^= PORT_INVEN_bm;
    }
    // Re-enable pin interrupt
    PORTA.INT1MASK = P_PWR_SENSE_bm;
}

//--------------------------------------------------------------------------------------------------
static void ev_switch_on();
static void ev_switch_off();
ISR(TCE0_CCB_vect){
    uint8_t mode;
    // Timer fully expired. Light switch has settled
    
    // Disable timer
    TCE0.CTRLA = TC_CLKSEL_OFF_gc;
    
    mode = edge_counter-1;
    
    if(   (((PORTA.PIN4CTRL & PORT_INVEN_bm) == 0) && ((PORTA.IN & P_PWR_SENSE_bm) == 0))
        ||(((PORTA.PIN4CTRL & PORT_INVEN_bm) != 0) && ((PORTA.IN & P_PWR_SENSE_bm) != 0))
        ){
        // Light switch is in ON state
        event_PushEvent(ev_switch_on, &mode, sizeof(mode));
    }else{
        // Light switch is in OFF state
        event_PushEvent(ev_switch_off, &mode, sizeof(mode));
        edge_counter = 0;
    }
    
}

//==================================================================================================
// Events
//==================================================================================================
static void ev_switch_on(){
    uint8_t mode;
    event_PopEventData(&mode, sizeof(mode));
    
    if(Cfg.current_modeset){
        mode = mode % Cfg.current_modeset->n;
        transition_start(Cfg.current_modeset->modes[mode].on);
    }else{
        // no configuration loaded. Do something sane
        rgbw_t rgbw;
        
        // Abort any transitions in progress
        transition_abort();
        
        rgbw.r = 0;
        rgbw.g = 0;
        rgbw.b = 0;
        rgbw.w = 0xFFFF;
        pwm_set_value(&rgbw);
    }
}

//--------------------------------------------------------------------------------------------------
static void ev_switch_off(){
    uint8_t mode;
    event_PopEventData(&mode, sizeof(mode));
    
    if(Cfg.current_modeset){
        mode = mode % Cfg.current_modeset->n;
        transition_start(Cfg.current_modeset->modes[mode].off);
    }else{
        // no configuration loaded. Do something sane
        rgbw_t rgbw;
        
        // Abort any transitions in progress
        transition_abort();
        
        rgbw.r = 0;
        rgbw.g = 0;
        rgbw.b = 0;
        rgbw.w = 0;
        pwm_set_value(&rgbw);
    }
}
