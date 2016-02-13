

#include <stdint.h>
#include <stddef.h>

void debug_init(void);
void debug_puts(char *s);
void debug_val(char *label, uint16_t n);
size_t debug_get_chunk(void *dst, size_t max);
