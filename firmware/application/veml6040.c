
#include <stdint.h>
#include <stddef.h>

#define F_CPU 32000000UL
#include <util/delay.h>

#include "veml6040.h"
#include <i2c.h>


#define VEML_SLAVE_ADDR (0x10)

#define VEML_CMD_CONF   0x00
#define VEML_CMD_RDATA  0x08
#define VEML_CMD_GDATA  0x09
#define VEML_CMD_BDATA  0x0A
#define VEML_CMD_WDATA  0x0B

// Conf register
#define VEML_DISABLE    0x01
#define VEML_FORCE_MODE 0x02
#define VEML_TRIG       0x04

void veml6040_init(void){
    i2c_init();
}

int veml6040_start_sample(uint8_t integ_time){
    i2c_package_t pkg;
    uint16_t timeout = 3000;
    
    pkg.slave_addr = VEML_SLAVE_ADDR;
    pkg.addr[0] = VEML_CMD_CONF;
    pkg.addr[1] = integ_time | VEML_FORCE_MODE | VEML_TRIG;
    pkg.addr_len = 2;
    pkg.data_len = 0;
    pkg.read = false;
    i2c_transfer_start(&pkg, NULL);
    
    while(i2c_transfer_status() == I2C_BUSY){
        _delay_ms(1);
        timeout--;
        if(timeout == 0){
            return(-1);
        }
    }
    
    return(0);
}

static uint16_t read_single(uint8_t reg_addr) {
    i2c_package_t pkg;
    uint8_t data[2];
    uint16_t result = 0;
    uint16_t timeout = 3000;
    
    pkg.slave_addr = VEML_SLAVE_ADDR;
    pkg.addr[0] = reg_addr;
    pkg.addr_len = 1;
    pkg.data = data;
    pkg.data_len = 2;
    pkg.read = true;
    i2c_transfer_start(&pkg, NULL);
    
    while(i2c_transfer_status() == I2C_BUSY){
        _delay_ms(1);
        timeout--;
        if(timeout == 0){
            return(0xFFFF);
        }
    }
    
    result = data[1];
    result <<= 8;
    result += data[0];
    return(result);
}

void veml6040_read_result(veml6040_sample_t *result){
    result->r = read_single(VEML_CMD_RDATA);
    result->g = read_single(VEML_CMD_GDATA);
    result->b = read_single(VEML_CMD_BDATA);
    result->w = read_single(VEML_CMD_WDATA);
}

int veml6040_sample(uint8_t integ_time, veml6040_sample_t *result){
    int res;
    res = veml6040_start_sample(integ_time);
    if(res) return(res);
    
    switch(integ_time){
        case VEML_IT_40MS:
            _delay_ms(40);
            break;
        case VEML_IT_80MS:
            _delay_ms(80);
            break;
        case VEML_IT_160MS:
            _delay_ms(160);
            break;
        case VEML_IT_320MS:
            _delay_ms(320);
            break;
        case VEML_IT_640MS:
            _delay_ms(640);
            break;
        case VEML_IT_1280MS:
            _delay_ms(1280);
            break;
    }
    
    veml6040_read_result(result);
    return(0);
}
