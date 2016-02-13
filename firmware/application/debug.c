
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include <fifo.h>
#include <string_ext.h>

#define DEBUGBUF_SIZE 128

static uint8_t DebugBuf[DEBUGBUF_SIZE] __attribute__ ((section (".noinit")));
static FIFO_t DebugFifo;

void debug_init(void){
    fifo_init(&DebugFifo, DebugBuf, sizeof(DebugBuf));
}

void debug_puts(char *s){
    fifo_write_trample(&DebugFifo, s, strlen(s));
}

void debug_val(char *label, uint16_t n){
    char buf[5];
    debug_puts(label);
    snprint_x16(buf,sizeof(buf),n);
    debug_puts(buf);
    debug_puts("\r\n");
}

size_t debug_get_chunk(void *dst, size_t max){
    return(fifo_read_max(&DebugFifo, dst, max));
}
