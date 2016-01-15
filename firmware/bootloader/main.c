
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <avr/fuse.h>

#include <cli.h>
#include <uart_io.h>
#include <bt_rn42.h>
#include <board.h>

#define F_CPU 32000000UL
#include <util/delay.h>

//--------------------------------------------------------------------------------------------------
FUSES = {
	0xFF,	// Fuse 0: (Reserved)
	0x00,	// Fuse 1: Watchdog cfg. Not using
	0xBF,	// Fuse 2: BOOTRST
	0xFF,	// Fuse 3 (Reserved)
	0xF2,	// Fuse 4: Max startup time
	0xFF	// Fuse 5: 
};

//--------------------------------------------------------------------------------------------------
void start_app(void);
static void init_clk(void);

//--------------------------------------------------------------------------------------------------
int main(void){
    // Stay in bootloader if software reset, OR pushbutton is being held.
    if((RST.STATUS != RST_SRF_bm) && ((PORTC.IN & P_BUTTON_bm) == 0)){
        // Reset was not requested by software AND pushbutton is not pressed
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
    
    // Initialize Bluetooth
    _delay_ms(250);
    if(RST.STATUS != RST_SRF_bm){
        // This was a hard reset
        // Bluetooth isn't guaranteed to be initialized
        _delay_ms(1000);
        bt_enter_cmd_mode();
        bt_S_cmd("SA,2\r");             // "Just Works" auth mode
        bt_S_cmd("SP,1234\r");          // Set pin in case some devices fall back to pin authentication.
        bt_S_cmd("S-,SkylightLED\r");   // Results in name SkylightLED-XXXX where XXXX is last 2-bytes of MAC
        bt_S_cmd("ST,253\r");           // Always configrable. Local config only
        bt_reboot();                    // Reboot for changes to take effect
        _delay_ms(250);
    }else{
        // Assume BT is configured. Set discoverable
        bt_enter_cmd_mode();
        bt_S_cmd("Q,0\r"); // discoverable and able to connect
        bt_exit_cmd_mode();
    }
    PORTA.OUTSET = P_LED_bm;
    
    
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
    PROTECTED_WRITE(CLK.CTRL, CLK_SCLKSEL_RC32M_gc);
    
    // Disable any prescaling
    PROTECTED_WRITE(CLK.PSCTRL, 0x00);
    
    // Disable unused oscillators
    OSC.CTRL &= ~(OSC_PLLEN_bm | OSC_RC32KEN_bm | OSC_RC2MEN_bm);
}
