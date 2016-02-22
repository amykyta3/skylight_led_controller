#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli.h>
#include <cli_commands.h>
#include <uart_io.h>
#include <board.h>
#include <rtc.h>
#include <string_ext.h>

#include "led_pwm.h"
#include "debug.h"
#include "eeprom_config.h"

//==================================================================================================
static uint16_t xtou16(char *s){
    uint16_t n = 0;
    while(*s){
        uint8_t nib;
        if(isdigit(*s)){
            nib = *s - '0';
        }else if((*s >= 'A') && (*s <= 'F')){
            nib = *s - 'A' + 10;
        }else if((*s >= 'a') && (*s <= 'f')){
            nib = *s - 'a' + 10;
        }else{
            return(n);
        }
        n <<= 4;
        n += nib;
        s++;
    }
    return(n);
}

static uint8_t hex2nibble(char c){
    if((c >= '0') && (c <= '9')){
        return(c-'0');
    }else if((c >= 'A') && (c <= 'F')){
        return(c-'A'+10);
    }else if((c >= 'a') && (c <= 'f')){
        return(c-'a'+10);
    }else{
        return(0);
    }
}

//==================================================================================================
// Device-specific output functions
//==================================================================================================

void cli_puts(char *str){
    uart_puts(str);
}

void cli_putc(char chr){
    uart_putc(chr);
}

void cli_print_prompt(void){
    uart_puts("\r\n>");
}

void cli_print_error(int error){
    uart_puts("ERR");
}

void cli_print_notfound(char *strcmd){
    uart_puts("ERR");
}

//==================================================================================================
// Custom Commands
//==================================================================================================
int cmd_id(uint8_t argc, char *argv[]){
    cli_puts("APP");
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_echo(uint8_t argc, char *argv[]){
    if(argc != 2) return(1);
    
    if(argv[1][0] == '1'){
        cli_echo_on();
    }else if(argv[1][0] == '0'){
        cli_echo_off();
    }else{
        return(1);
    }
    return(0);
}
//--------------------------------------------------------------------------------------------------
int cmd_reset(uint8_t argc, char *argv[]){
    // Disable Interrupt
    cli();
    
    // Reset
    PROTECTED_WRITE(RST.CTRL, RST_SWRST_bm);
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_rgbw(uint8_t argc, char *argv[]){
    rgbw_t rgbw;
    if(argc != 5) return(1);
    
    rgbw.r = xtou16(argv[1]);
    rgbw.g = xtou16(argv[2]);
    rgbw.b = xtou16(argv[3]);
    rgbw.w = xtou16(argv[4]);
    pwm_set_value(&rgbw);
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_get_time(uint8_t argc, char *argv[]){
    calendar_time_t T;
    char tmp[5];
    
    calendar_get_time(&T);
    
    snprint_x8(tmp,sizeof(tmp),T.dayofweek);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x16(tmp,sizeof(tmp),T.year);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x8(tmp,sizeof(tmp),T.month);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x8(tmp,sizeof(tmp),T.day);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x8(tmp,sizeof(tmp),T.hour);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x8(tmp,sizeof(tmp),T.minute);
    cli_puts(tmp);
    cli_putc(' ');
    
    snprint_x8(tmp,sizeof(tmp),T.second);
    cli_puts(tmp);
    
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_set_time(uint8_t argc, char *argv[]){
    calendar_time_t T;
    
    if(argc != 7) return(1);
    T.dayofweek = UNKNOWN_DOW;
    T.year      = xtou16(argv[1]);
    T.month     = xtou16(argv[2]);
    T.day       = xtou16(argv[3]);
    T.hour      = xtou16(argv[4]);
    T.minute    = xtou16(argv[5]);
    T.second    = xtou16(argv[6]);
    calendar_set_time(&T);
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_set_dst(uint8_t argc, char *argv[]){
    if(argc != 3) return(1);
    calendar_set_DST(xtou16(argv[1]), xtou16(argv[2]));
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_cfg_erase(uint8_t argc, char *argv[]){
    eecfg_unload_cfg();
    eecfg_erase();
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_cfg_write(uint8_t argc, char *argv[]){
    uint8_t page;
    uint8_t data[EEPROM_PAGE_SIZE];
    
    if(argc != 3) return(1);
    
    page = xtou16(argv[1]);
    if(page >= EEPROM_PAGE_COUNT) return(1);
    
    if(strlen(argv[2]) != EEPROM_PAGE_SIZE*2) return(1);
    for(uint8_t i=0; i<EEPROM_PAGE_SIZE; i++){
        data[i] = hex2nibble(argv[2][i*2]);
        data[i] <<= 4;
        data[i] += hex2nibble(argv[2][i*2+1]);
    }
    
    eecfg_write_page(page, data);
    
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_cfg_reload(uint8_t argc, char *argv[]){
    eecfg_reload_cfg();
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_cfg_read(uint8_t argc, char *argv[]){
    uint16_t address;
    uint8_t page;
    uint8_t *data;
    
    if(argc != 2) return(1);
    
    page = xtou16(argv[1]);
    if(page >= EEPROM_PAGE_COUNT) return(1);
    address = page;
    address *= EEPROM_PAGE_SIZE;
    address += MAPPED_EEPROM_START;
    data = (uint8_t*) address;
    
    for(uint8_t i=0; i<EEPROM_PAGE_SIZE; i++){
        char tmp[3];
        snprint_x8(tmp,sizeof(tmp),data[i]);
        cli_puts(tmp);
    }
    
    return(0);
}

//--------------------------------------------------------------------------------------------------

int cmd_xxx(uint8_t argc, char *argv[]){
    rgbw_t end;
    
    if(argc != 6) return(1);
    
    for(uint8_t i=0; i<4; i++){
        end.arr[i] = xtou16(argv[1+i]);
    }
    
    pwm_start_fade(&end, xtou16(argv[5]));

    return(0);
}
