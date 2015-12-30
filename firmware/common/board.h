#ifndef BOARD_H
#define BOARD_H

#include <avr/io.h>

// Port A
#define P_BT_GPIO3_bm   PIN0_bm
#define P_BT_GPIO4_bm   PIN1_bm
#define P_LED_bm        PIN2_bm
#define P_PWR_SENSE_bm  PIN4_bm
#define P_BT_CTS_bm     PIN5_bm
#define P_BT_RTS_bm     PIN6_bm
#define P_BT_AUTO_DSC_MODE_bm   P_BT_GPIO3_bm
#define P_BT_FACTORY_RST        P_BT_GPIO4_bm
#define P_PA_UNUSED_bm  (PIN3_bm | PIN7_bm)

// Port B
#define P_PB_UNUSED_bm  (PIN0_bm | PIN1_bm | PIN2_bm | PIN3_bm)

// Port C
#define P_I2C0_SDA_bm   PIN0_bm
#define P_I2C0_SCL_bm   PIN1_bm
#define P_BT_RX_bm      PIN2_bm
#define P_BT_TX_bm      PIN3_bm
#define P_BUTTON_bm     PIN5_bm
#define P_BT_GPIO6_bm   PIN6_bm
#define P_BT_RESETN_bm  PIN7_bm
#define P_BT_SET_MASTER P_BT_GPIO6_bm
#define P_PC_UNUSED_bm  (PIN4_bm)

// Port D
#define P_PWM_R_bm      PIN0_bm
#define P_PWM_G_bm      PIN1_bm
#define P_PWM_B_bm      PIN2_bm
#define P_PWM_W_bm      PIN3_bm
#define P_PD_UNUSED_bm  (PIN4_bm | PIN5_bm | PIN6_bm | PIN7_bm)

// Port E
#define P_I2C1_SDA_bm   PIN0_bm
#define P_I2C1_SCL_bm   PIN1_bm
#define P_PE_UNUSED_bm  (PIN2_bm | PIN3_bm)

// Port R

#endif