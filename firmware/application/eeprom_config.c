
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <avr/io.h>

#include <rtc.h>
#include <uart_io.h>
#include <uart_io_ext.h>

#include "timestamp.h"
#include "led_transitions.h"
#include "eeprom_config.h"

#define NVM_EXEC()	asm("push r30"      "\n\t"	\
                        "push r31"      "\n\t"	\
                        "push r16"      "\n\t"	\
                        "push r18"      "\n\t"	\
                        "ldi r30, 0xCB" "\n\t"	\
                        "ldi r31, 0x01" "\n\t"	\
                        "ldi r16, 0xD8" "\n\t"	\
                        "ldi r18, 0x01" "\n\t"	\
                        "out 0x34, r16" "\n\t"	\
                        "st Z, r18"	    "\n\t"	\
                        "pop r18"       "\n\t"	\
                        "pop r16"       "\n\t"	\
                        "pop r31"       "\n\t"	\
                        "pop r30"       "\n\t"	\
                        )

//==============================================================================
// Shared variables
//==============================================================================
Cfg_t Cfg;

//==============================================================================
// Internal
//==============================================================================
void cb_lighting_alarm(void *data){
    // Alarm fired to do a lighting event
    transition_start(data);
}

void cb_modeset_change(void *data){
    // Alarm fired to switch modesets
    Cfg.current_modeset = data;
}

//==============================================================================
// Functions
//==============================================================================
void eecfg_init(void){
    
    // Enable memory-mapped EEPROM
    NVM.CTRLB |= NVM_EEMAPEN_bm;
    
    // Ensure Cfg is cleared
    Cfg.current_modeset = NULL;
    Cfg.n_alarms = 0;
    Cfg.alarms = NULL;
    
    eecfg_reload_cfg();
}

//------------------------------------------------------------------------------
void eecfg_unload_cfg(void){
    
    // Abort any transitions in progress
    transition_abort();
    
    Cfg.current_modeset = NULL;
    
    // Stop any alarms
    for(uint8_t i=0; i<Cfg.n_alarms; i++){
        calendar_remove_alarm(&Cfg.alarms[i]);
    }
    free(Cfg.alarms);
    Cfg.alarms = NULL;
    Cfg.n_alarms = 0;
}

//------------------------------------------------------------------------------
void eecfg_reload_cfg(void){
    
    eecfg_unload_cfg();
    
    if(eeConfig.timestamp == Build_Timestamp){
        // Configuration is valid. Load!
        
        Cfg.current_modeset = eeConfig.default_modeset;
        
        // Malloc space for alarms
        Cfg.n_alarms  = eeConfig.lighting_alarm_table->n;
        Cfg.n_alarms += eeConfig.modeset_change_table->n;
        Cfg.alarms = malloc(sizeof(calendar_alarm_t) * (Cfg.n_alarms));
        
        // Register alarms
        for(uint8_t i=0; i<eeConfig.lighting_alarm_table->n; i++){
            uint16_t a_idx = i;
            Cfg.alarms[a_idx].dayofweek_mask = eeConfig.lighting_alarm_table->alarms[i].dayofweek_mask;
            Cfg.alarms[a_idx].hour = eeConfig.lighting_alarm_table->alarms[i].hour;
            Cfg.alarms[a_idx].minute = eeConfig.lighting_alarm_table->alarms[i].minute;
            Cfg.alarms[a_idx].callback = cb_lighting_alarm;
            Cfg.alarms[a_idx].callback_data = eeConfig.lighting_alarm_table->alarms[i].transition;
            calendar_add_alarm(&Cfg.alarms[a_idx]);
        }
        for(uint8_t i=0; i<eeConfig.modeset_change_table->n; i++){
            uint16_t a_idx = i;
            a_idx += eeConfig.lighting_alarm_table->n;
            Cfg.alarms[a_idx].dayofweek_mask = eeConfig.modeset_change_table->alarms[i].dayofweek_mask;
            Cfg.alarms[a_idx].hour = eeConfig.modeset_change_table->alarms[i].hour;
            Cfg.alarms[a_idx].minute = eeConfig.modeset_change_table->alarms[i].minute;
            Cfg.alarms[a_idx].callback = cb_modeset_change;
            Cfg.alarms[a_idx].callback_data = eeConfig.modeset_change_table->alarms[i].modeset;
            calendar_add_alarm(&Cfg.alarms[a_idx]);
        }
    }
}

//------------------------------------------------------------------------------
void eecfg_erase(void){
    memset((void*)MAPPED_EEPROM_START,0xFF, EEPROM_PAGE_SIZE);
    
    NVM.CMD = NVM_CMD_ERASE_EEPROM_gc;
    NVM_EXEC();
    while(NVM.STATUS & NVM_NVMBUSY_bm);
}

//------------------------------------------------------------------------------
void eecfg_write_page(uint8_t page, void *data){
    uint16_t address;
    
    address = MAPPED_EEPROM_START;
    address += (uint16_t) page*EEPROM_PAGE_SIZE;
    
    // Load buffer
    if(page == 0){
        // Page 0 is header. Replace first 4 bytes with timestamp
        uint32_t *timestamp;
        timestamp = (uint32_t *)MAPPED_EEPROM_START;
        *timestamp = Build_Timestamp;
        
        // Copy remainder of page
        address = MAPPED_EEPROM_START + 4;
        data += 4;
        memcpy((void*)address, data, EEPROM_PAGE_SIZE-4);
    }else{
        memcpy((void*)address, data, EEPROM_PAGE_SIZE);
    }
    
    // Page address is zero-based. remove mapped offset
    address -= MAPPED_EEPROM_START;

	// Perform write
	NVM.ADDR0 = address & 0xFF;
	NVM.ADDR1 = (address >> 8) & 0x1F;
	NVM.ADDR2 = 0x00;
	NVM.CMD = NVM_CMD_WRITE_EEPROM_PAGE_gc;
	NVM_EXEC();
    
    while(NVM.STATUS & NVM_NVMBUSY_bm);
}

//==============================================================================
// Config Printer
// Print the contents of the config for debug
//==============================================================================

static void print_newline(uint8_t indent){
    uart_puts("\r\n");
    while(indent){
        uart_putc(' ');
        indent--;
    }
}

static void print_color_list(color_list_t *o, uint8_t indent){
    print_newline(indent);
    uart_putc('[');
    
    for(uint8_t i=0; i < o->n; i++){
        print_newline(indent+1);
        uart_putc('(');
        uart_put_x16(o->colors[i].r);
        uart_putc(',');
        uart_put_x16(o->colors[i].g);
        uart_putc(',');
        uart_put_x16(o->colors[i].b);
        uart_putc(',');
        uart_put_x16(o->colors[i].w);
        uart_putc(')');
    }
    
    print_newline(indent);
    uart_putc(']');
}

static void print_transition(transition_t *o, uint8_t indent){
    print_newline(indent);
    uart_putc('{');
    
    print_newline(indent+1);
    uart_puts("delay: ");
    uart_put_d16(o->delay);
    
    switch(o->type){
        case TRANS_IMMEDIATE:
            print_newline(indent+1);
            uart_puts("type: immediate");
            
            print_newline(indent+1);
            uart_puts("color: (");
            uart_put_x16(o->immediate.color.r);
            uart_putc(',');
            uart_put_x16(o->immediate.color.g);
            uart_putc(',');
            uart_put_x16(o->immediate.color.b);
            uart_putc(',');
            uart_put_x16(o->immediate.color.w);
            uart_putc(')');
            
            break;
        case TRANS_FADE:
            print_newline(indent+1);
            uart_puts("type: fade");
            
            print_newline(indent+1);
            uart_puts("color: (");
            uart_put_x16(o->fade.color.r);
            uart_putc(',');
            uart_put_x16(o->fade.color.g);
            uart_putc(',');
            uart_put_x16(o->fade.color.b);
            uart_putc(',');
            uart_put_x16(o->fade.color.w);
            uart_putc(')');
            
            print_newline(indent+1);
            uart_puts("duration: ");
            uart_put_d16(o->fade.duration);
            
            break;
        case TRANS_WAVEFORM:
            print_newline(indent+1);
            uart_puts("type: waveform");
            
            print_newline(indent+1);
            uart_puts("waveform: @");
            uart_put_x16((uint16_t)o->waveform.waveform);
            print_color_list(o->waveform.waveform, indent+2);
            
            print_newline(indent+1);
            uart_puts("duration: ");
            uart_put_d16(o->waveform.duration);
            
            break;
    }
    
    print_newline(indent);
    uart_putc('}');
}

static void print_modeset(modeset_t *o, uint8_t indent){
    print_newline(indent);
    uart_putc('[');
    for(uint8_t i=0; i < o->n; i++){
        print_newline(indent+1);
        uart_putc('{');
        
        print_newline(indent+2);
        uart_puts("on: @");
        uart_put_x16((uint16_t)o->modes[i].on);
        print_transition(o->modes[i].on, indent+3);
        
        print_newline(indent+2);
        uart_puts("off: @");
        uart_put_x16((uint16_t)o->modes[i].off);
        print_transition(o->modes[i].off, indent+3);
        
        print_newline(indent+1);
        uart_putc('}');
    }
    print_newline(indent);
    uart_putc(']');
}

static void print_lighting_alarm_table(lighting_alarm_table_t *o, uint8_t indent){
    print_newline(indent);
    uart_putc('[');
    
    for(uint8_t i=0; i < o->n; i++){
        print_newline(indent+1);
        uart_putc('{');
        
        print_newline(indent+2);
        uart_puts("DOW: ");
        uart_put_x8(o->alarms[i].dayofweek_mask);
        
        print_newline(indent+2);
        uart_puts("hour: ");
        uart_put_d8(o->alarms[i].hour);
        
        print_newline(indent+2);
        uart_puts("minute: ");
        uart_put_d8(o->alarms[i].minute);
        
        print_newline(indent+2);
        uart_puts("transition: @");
        uart_put_x16((uint16_t)o->alarms[i].transition);
        print_transition(o->alarms[i].transition, indent+3);
        
        print_newline(indent+1);
        uart_putc('}');
    }
    
    print_newline(indent);
    uart_putc(']');
}

static void print_modeset_change_table(modeset_change_table_t *o, uint8_t indent){
    print_newline(indent);
    uart_putc('[');
    
    for(uint8_t i=0; i < o->n; i++){
        print_newline(indent+1);
        uart_putc('{');
        
        print_newline(indent+2);
        uart_puts("DOW: ");
        uart_put_x8(o->alarms[i].dayofweek_mask);
        
        print_newline(indent+2);
        uart_puts("hour: ");
        uart_put_d8(o->alarms[i].hour);
        
        print_newline(indent+2);
        uart_puts("minute: ");
        uart_put_d8(o->alarms[i].minute);
        
        print_newline(indent+2);
        uart_puts("modeset: @");
        uart_put_x16((uint16_t)o->alarms[i].modeset);
        print_modeset(o->alarms[i].modeset, indent+3);
        
        print_newline(indent+1);
        uart_putc('}');
    }
    
    print_newline(indent);
    uart_putc(']');
}

int eecfg_print_me(void){
    
    if(eeConfig.timestamp == Build_Timestamp){
        print_newline(0);
        uart_puts("default_modeset: @");
        uart_put_x16((uint16_t)eeConfig.default_modeset);
        print_modeset(eeConfig.default_modeset, 1);
        
        print_newline(0);
        uart_puts("lighting_alarm_table: @");
        uart_put_x16((uint16_t)eeConfig.lighting_alarm_table);
        print_lighting_alarm_table(eeConfig.lighting_alarm_table, 1);
        
        print_newline(0);
        uart_puts("modeset_change_table: @");
        uart_put_x16((uint16_t)eeConfig.modeset_change_table);
        print_modeset_change_table(eeConfig.modeset_change_table, 1);
        return(0);
    }else{
        return(-1);
    }
}
