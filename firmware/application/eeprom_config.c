
#include <stdint.h>
#include <string.h>
#include <avr/io.h>

#include "timestamp.h"

#define NVM_EXEC()	asm("push r30"      "\n\t"	\
                        "push r31"      "\n\t"	\
                        "push r16"      "\n\t"	\
                        "push r18"      "\n\t"	\
                        "ldi r30, 0xCB" "\n\t"	\
                        "ldi r31, 0x01" "\n\t"	\
                        "ldi r16, 0xD8" "\n\t"	\
                        "ldi r18, 0x01" "\n\t"	\
                        "out 0x34, r16" "\n\t"	\
                        "st Z, r18"	    "\n\t"	\
                        "pop r18"       "\n\t"	\
                        "pop r16"       "\n\t"	\
                        "pop r31"       "\n\t"	\
                        "pop r30"       "\n\t"	\
                        )

//------------------------------------------------------------------------------
void eecfg_init(void){
    
    // Enable memory-mapped EEPROM
    NVM.CTRLB |= NVM_EEMAPEN_bm;
}

//------------------------------------------------------------------------------
void eecfg_erase(void){
    memset((void*)MAPPED_EEPROM_START,0xFF, EEPROM_PAGE_SIZE);
    
    NVM.CMD = NVM_CMD_ERASE_EEPROM_gc;
    NVM_EXEC();
    while(NVM.STATUS & NVM_NVMBUSY_bm);
}

//------------------------------------------------------------------------------
void eecfg_write_page(uint8_t page, void *data){
    uint16_t address;
    
    address = MAPPED_EEPROM_START;
    address += (uint16_t) page*EEPROM_PAGE_SIZE;
    
    // Load buffer
    if(page == 0){
        // Page 0 is header. Replace first 4 bytes with timestamp
        uint32_t *timestamp;
        timestamp = (uint32_t *)MAPPED_EEPROM_START;
        *timestamp = Build_Timestamp;
        
        // Copy remainder of page
        address = MAPPED_EEPROM_START + 4;
        data += 4;
        memcpy((void*)address, data, EEPROM_PAGE_SIZE-4);
    }else{
        memcpy((void*)address, data, EEPROM_PAGE_SIZE);
    }
    
    // Page address is zero-based. remove mapped offset
    address -= MAPPED_EEPROM_START;

	// Perform write
	NVM.ADDR0 = address & 0xFF;
	NVM.ADDR1 = (address >> 8) & 0x1F;
	NVM.ADDR2 = 0x00;
	NVM.CMD = NVM_CMD_WRITE_EEPROM_PAGE_gc;
	NVM_EXEC();
    
    while(NVM.STATUS & NVM_NVMBUSY_bm);
}
