
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
void blink_n(int n){
    int count = n;
    while(count){
        PORTA.OUTSET = P_LED_bm;
        _delay_ms(250);
        PORTA.OUTCLR = P_LED_bm;
        _delay_ms(250);
        count--;
    }
}
//--------------------------------------------------------------------------------------------------
void err(int n){
    while(1){
        _delay_ms(2000);
        blink_n(n);
    }
}

//--------------------------------------------------------------------------------------------------
int main(void){
    uint8_t rst_status;
    
    // Capture reset status and clear
    rst_status = RST.STATUS;
    RST.STATUS = 0xFF;
    
    // Stay in bootloader if software reset, OR pushbutton is being held.
    if((rst_status != RST_SRF_bm) && ((PORTC.IN & P_BUTTON_bm) == 0)){
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
    
    _delay_ms(250);
    
    uart_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm;
    sei();
    
    // Initialize Bluetooth
    if(rst_status != RST_SRF_bm){
        // This was a hard reset
        // Bluetooth isn't guaranteed to be initialized
        blink_n(2);
        //_delay_ms(1000);
        if(bt_enter_cmd_mode()) err(1);
        if(bt_S_cmd("SA,2\r")) err(2);             // "Just Works" auth mode
        if(bt_S_cmd("SP,1234\r")) err(3);          // Set pin in case some devices fall back to pin authentication.
        if(bt_S_cmd("S-,SkylightLED\r")) err(4);   // Results in name SkylightLED-XXXX where XXXX is last 2-bytes of MAC
        if(bt_S_cmd("ST,253\r")) err(5);           // Always configrable. Local config only
        if(bt_reboot()) err(6);                    // Reboot for changes to take effect
        //_delay_ms(250);
    }else{
        blink_n(1);
        // Assume BT is configured. Set discoverable
        if(bt_enter_cmd_mode()) err(7);
        if(bt_S_cmd("Q,0\r")) err(8); // discoverable and able to connect
        bt_exit_cmd_mode();
    }
    PORTA.OUTSET = P_LED_bm;
    
    
    while(1){
        char c;
        c = uart_getc();
        PORTA.OUTTGL = P_LED_bm;
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
