
#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli_commands.h>
#include <uart_io.h>

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
void start_app(void);

int cmd_boot(uint16_t argc, char *argv[]){
    start_app();
    return(1); // if got here, boot failed
}

//--------------------------------------------------------------------------------------------------
int cmd_id(uint16_t argc, char *argv[]){
    cli_puts("BL");
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_reset(uint16_t argc, char *argv[]){
    // Disable Interrupt
    cli();
    
    // Reset
    PROTECTED_WRITE(RST.CTRL, RST_SWRST_bm);
    return(0);
}
