
#include <avr/io.h>

#include "board.h"

/**
 * \brief Low-level init routine
 * \details This routine is automatically linked to execute immediately after power-up
 * This routine is only to set initial "Safe" IO settings
 *  - Pin direction
 *  - Initial value for outputs
 * 
 * \warning Since this executes prior to crt0 (initialization of the C Runtime environment), 
 * function calls, allocation of variables, etc may not work yet. Also, do not call this function
 * since it does not use the usual return convention.
 **/
void __init0(void) __attribute__((naked)) __attribute__ ((section (".init0")));
void __init0(void){
    
    // Port A
    PORTA.PIN2CTRL = PORT_INVEN_bm; // Invert LED pin
    PORTA.DIR = P_LED_bm | P_BT_AUTO_DSC_MODE_bm | P_BT_FACTORY_RST | P_BT_RTS_bm;
    PORTA.OUT = 0x00;
    PORTA.INTCTRL = 0x00;
    PORTA.INT0MASK = 0x00;
    PORTA.INT1MASK = 0x00;
    
    // Port B
    PORTB.DIR = 0x00;
    PORTB.OUT = 0x00;
    
    // Port C
    PORTC.PIN5CTRL = PORT_INVEN_bm | PORT_OPC_PULLUP_gc; // Pushbutton
    PORTC.DIR = P_BT_TX_bm | P_BT_RESETN_bm | P_BT_SET_MASTER;
    PORTC.OUT = P_BT_TX_bm | P_BT_RESETN_bm;
    PORTC.INTCTRL = 0x00;
    PORTC.INT0MASK = 0x00;
    PORTC.INT1MASK = 0x00;
    
    // Port D
    PORTD.DIR = P_PWM_R_bm | P_PWM_G_bm | P_PWM_B_bm | P_PWM_W_bm;
    PORTD.OUT = 0x00;
    PORTD.INTCTRL = 0x00;
    PORTD.INT0MASK = 0x00;
    PORTD.INT1MASK = 0x00;
    
    // Port E
    PORTE.DIR = 0x00;
    PORTE.OUT = 0x00;
    PORTE.INTCTRL = 0x00;
    PORTE.INT0MASK = 0x00;
    PORTE.INT1MASK = 0x00;
    
    // Safe settings for unused pins
    PORTA.PIN3CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTA.PIN7CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTB.PIN0CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTB.PIN1CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTB.PIN2CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTB.PIN3CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTC.PIN4CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTD.PIN4CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTD.PIN5CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTD.PIN6CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTD.PIN7CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTE.PIN2CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
    PORTE.PIN3CTRL = PORT_OPC_PULLDOWN_gc | PORT_ISC_INPUT_DISABLE_gc;
}
