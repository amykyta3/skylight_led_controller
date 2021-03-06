
#ifndef RTC_CONFIG_H
#define RTC_CONFIG_H

#define RTC_CLOCK_SOURCE    1
    // 0 = 1 kHz from internal 32kHz ULP
    // 1 = 1.024 kHz from 32.768 kHz crystal oscillator on TOSC
    // 2 = 1.024 kHz from 32.768 kHz internal oscillator
    // 3 = 32.768 kHz from 32.768 kHz crystal oscillator on TOSC
    // 4 = 32.768 kHz from 32.768 kHz internal oscillator

#define RTC_PRESCALER       16
    // 1, 2, 8, 16, 64, 256, 1024
    
// Results in:
//  15.625 ms/tick
//  1-sec = 64 ticks

#define RTC_OVFINTLVL       RTC_OVFINTLVL_HI_gc
#define RTC_COMPINTLVL      RTC_COMPINTLVL_HI_gc

#define RTC_CALENDAR_ENABLE 1
#define RTC_TIMER_ENABLE    1

#endif
