#ifndef EEPROM_CONFIG_H
#define EEPROM_CONFIG_H

#include <stdint.h>
#include <avr/io.h>

#include <rtc.h>
#include "led_pwm.h"

#define EEPROM_PAGE_COUNT (EEPROM_SIZE/EEPROM_PAGE_SIZE)

//==============================================================================
// EEPROM Configuration Objects
//==============================================================================

// Tranition Types
#define TRANS_IMMEDIATE 0
#define TRANS_FADE      1
#define TRANS_WAVEFORM  2

typedef struct {
    uint8_t n;
    rgbw_t colors[0];
} color_list_t;

typedef struct {
    uint8_t type;
    uint16_t delay;
    union {
        struct {
            rgbw_t color;
        } immediate;
        
        struct {
            rgbw_t color;
            uint16_t duration;
        } fade;
        
        struct {
            color_list_t *waveform;
            uint16_t duration;
        } waveform;
    };
} transition_t;

typedef struct {
    uint8_t n;
    struct {
        transition_t *on;
        transition_t *off;
    } modes[0];
} modeset_t;

typedef struct {
    uint8_t n;
    struct {
        uint8_t dayofweek_mask;
        uint8_t hour;
        uint8_t minute;
        transition_t *transition;
    } alarms[0];
} lighting_alarm_table_t;

typedef struct {
    uint8_t n;
    struct {
        uint8_t dayofweek_mask;
        uint8_t hour;
        uint8_t minute;
        modeset_t *modeset;
    } alarms[0];
} modeset_change_table_t;

typedef struct {
    uint32_t timestamp;
    modeset_t *default_modeset;
    lighting_alarm_table_t *lighting_alarm_table;
    modeset_change_table_t *modeset_change_table;
} ee_config_t;

#define eeConfig (*(ee_config_t *) MAPPED_EEPROM_START)

//==============================================================================
// Loaded Configuration
//==============================================================================
typedef struct {
    modeset_t *current_modeset;
    uint16_t n_alarms;
    calendar_alarm_t *alarms;
} Cfg_t;
extern Cfg_t Cfg;

//==============================================================================
// Functions
//==============================================================================

/**
 * \brief Initialize EEPROM & load configuration
 **/
void eecfg_init(void);

/**
 * \brief Uninitialize previous configuration and reload new.
 **/
void eecfg_reload_cfg(void);

/**
 * \brief Uninitialize configuration
 **/
void eecfg_unload_cfg(void);

/**
 * Erases entire EEPROM
 **/
void eecfg_erase(void);

/**
 * \brief Write a 32-byte page to EEPROM
 * Assumes the page has already been erased
 **/
void eecfg_write_page(uint8_t page, void *data);

#endif
