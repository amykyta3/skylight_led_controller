#ifndef LED_TRANSITIONS_H
#define LED_TRANSITIONS_H

#include "eeprom_config.h"

/**
 * \brief Initialize transition handler
 **/
void transition_init(void);

/**
 * \brief Starts an LED transition effect
 * \param transition Pointer to transition object to execute
 **/
void transition_start(transition_t *transition);

/**
 * \brief Aborts any transitions in progress
 **/
void transition_abort(void);

#endif
