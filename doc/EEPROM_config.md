# EEPROM Configuration

All user-specific settings are stored in on-chip EEPROM.
These settings include:
* Lighting transitions
* Alarm events
* Modeset settings and switch alarms
* Clock compensation

## Misc

### EEPROM Pointers

Objects are referenced to each other within the EEPROM using pointers.

When writing these pointers to the EEPROM they shall be consistent with
the mapped address space of the AVR's EEPROM.

### Endianness

TBD. Conform to avr's endianness

### Packing

TBD. Conform to whatever avr-gcc's default struct packing behavior is.

## EEPROM Data structure

See the following file: [eeprom_config.h](../firmware/application/eeprom_config.h)
