#ifndef EEPROM_CONFIG_H
#define EEPROM_CONFIG_H

#include <stdint.h>
#include <avr/io.h>

#define EEPROM_PAGE_COUNT (EEPROM_SIZE/EEPROM_PAGE_SIZE)

typedef uint16_t eeptr_t;


void eecfg_init(void);

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
