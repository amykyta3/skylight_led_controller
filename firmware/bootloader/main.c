
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>

#include <cli.h>
#include <uart_io.h>
#include <board.h>

//--------------------------------------------------------------------------------------------------
void start_app(void);
static void init_clk(void);

//--------------------------------------------------------------------------------------------------
int main(void){
    
    if((RST.STATUS != RST_SRF_bm) && ((PORTC.IN & P_BUTTON_bm) == 0)){
        // No bootloader requested.
        // Try to boot app
        start_app();
        
        // If falls through, application does not exist.
    }
    
    // Staying in bootloader.
    
    // Set PMIC to use the bootloader IVEC table
    PROTECTED_WRITE(PMIC.CTRL, PMIC.CTRL | PMIC_IVSEL_bm);
    
    init_clk();
    uart_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm;
    sei();
    
    // If this was a hard reset
    if(RST.STATUS != RST_SRF_bm){
        // Bluetooth isn't guaranteed to be initialized
        //++ Reset & Init Bluetooth in discoverable mode
    }
    
    while(1){
        char c;
        c = uart_getc();
        cli_process_char(c);
    }
}

//--------------------------------------------------------------------------------------------------
void start_app(void){
    void(* app_entry)(void);
    
    // Read from flash address 0. If it has been programmed it won't be all 1's
    if(pgm_read_dword(0) == 0xFFFFFFFFUL){
        // Flash address is empty. Stay in bootloader
        return;
    }else{
        // Application exists. Safe to boot.
        
        // Disable interrupts and uninit stuff.
        cli();
        uart_uninit();
        
        // Set PMIC to use the application IVEC table
        PROTECTED_WRITE(PMIC.CTRL,PMIC.CTRL & ~PMIC_IVSEL_bm);
        
        EIND = 0;
        
        app_entry = 0; // App starts at address 0
        app_entry(); // Doesn't return
    }
}

//--------------------------------------------------------------------------------------------------
static void init_clk(void){
    
    // Init 32.768 kHz osc
    OSC.XOSCCTRL = OSC_X32KLPM_bm | OSC_XOSCSEL_32KHz_gc;
    OSC.CTRL |= OSC_XOSCEN_bm;
    while((OSC.STATUS & OSC_XOSCRDY_bm) == 0);
    
    // Init 32M osc to use DFLL reference to 32k external osc
    OSC.CTRL |= OSC_RC32MEN_bm;
    OSC.DFLLCTRL = OSC_RC32MCREF_XOSC32K_gc | OSC_RC2MCREF_XOSC32K_gc;
    DFLLRC32M.COMP1 = 0x12; // (32 MHz)/(1.024 kHz) = 0x7A12
    DFLLRC32M.COMP2 = 0x7A;
    DFLLRC32M.CTRL = DFLL_ENABLE_bm;
    
    // Select 32M Osc as sys clk
    CLK.CTRL = CLK_SCLKSEL_RC32K_gc;
    
    // Disable any prescaling
    CLK.PSCTRL = 0x00;
    
    // Disable unused oscillators
    OSC.CTRL &= ~(OSC_PLLEN_bm | OSC_RC32KEN_bm | OSC_RC2MEN_bm);
}
//--------------------------------------------------------------------------------------------------