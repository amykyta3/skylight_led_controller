########################################## Project Setup ###########################################

ECHO:=echo
CC:=avr-gcc
OBJCOPY:=avr-objcopy

PROJECT_NAME:=bootloader
BUILD_PATH:=build/
COMMON_SRC_PATH:=../common/

# Bootloader section byte address (NOT word address)
BOOTSTART:=0x20000

MCU:=atxmega128d4
INCLUDES:= $(COMMON_SRC_PATH) $(COMMON_SRC_PATH)atxmega_modules/src/ config
CFLAGS:= -Os -Wall -std=gnu99 -ffunction-sections -fdata-sections -g
LDFLAGS:= -Wl,--gc-sections,--section-start=.text=$(BOOTSTART) -Wl,-Map,$(BUILD_PATH)$(PROJECT_NAME).map -g
EXECUTABLE:= $(PROJECT_NAME).elf

SRC:= main.c
SRC+= cli_commands.c

COMMON_SRC:= init0.c
COMMON_SRC+= bt_rn42.c
COMMON_SRC+= atxmega_modules/src/fifo.c
COMMON_SRC+= atxmega_modules/src/uart_io.c
COMMON_SRC+= atxmega_modules/src/cli.c
COMMON_SRC+= atxmega_modules/src/intel_hex.c
COMMON_SRC+= atxmega_modules/src/self_program.c

####################################################################################################

all:$(EXECUTABLE)

dump_fuse:
	avrdude -q -q -p x128d4 -c avrispmkII -U fuse1:r:fuse1.hex:i
	avrdude -q -q -p x128d4 -c avrispmkII -U fuse2:r:fuse2.hex:i
	avrdude -q -q -p x128d4 -c avrispmkII -U fuse4:r:fuse4.hex:i
	avrdude -q -q -p x128d4 -c avrispmkII -U fuse5:r:fuse5.hex:i
	
dump_flash:
	avrdude -p x128d4 -c avrispmkII -U flash:r:flash.hex:i
	avrdude -p x128d4 -c avrispmkII -U boot:r:boot.hex:i
	
program:$(EXECUTABLE)
	@avrdude -q -q -p x128d4 -c avrispmkII -e
	@avrdude -q -q -p x128d4 -c avrispmkII -U boot:w:$<:e

erase:
	@avrdude -q -q -p x128d4 -c avrispmkII -e
	
fuse:$(EXECUTABLE)
	@avrdude -q -q -p x128d4 -c avrispmkII -U fuse1:w:$<:e -U fuse2:w:$<:e -U fuse4:w:$<:e -U fuse5:w:$<:e

disassemble:$(EXECUTABLE)
	avr-objdump -d -S $< > disassembly.S

########################################### AVR Compile ############################################

COMMON_BUILD_PATH:= $(BUILD_PATH)common/
OBJECTS:= $(addprefix $(BUILD_PATH),$(addsuffix .o,$(basename $(SRC))))
OBJECTS+= $(addprefix $(COMMON_BUILD_PATH),$(addsuffix .o,$(basename $(COMMON_SRC))))
DEPEND:= $(OBJECTS:.o=.d)

# Generate Dependencies
$(BUILD_PATH)%.d: %.c
	@mkdir -p $(dir $@)
	@$(CC) -MM -MT $(@:.d=.o) -MT $@ -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) $< >$@
	
$(COMMON_BUILD_PATH)%.d: $(COMMON_SRC_PATH)%.c
	@mkdir -p $(dir $@)
	@$(CC) -MM -MT $(@:.d=.o) -MT $@ -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) $< >$@
	
# C Compile
$(BUILD_PATH)%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) -c -o $@ $<
	
$(COMMON_BUILD_PATH)%.o: $(COMMON_SRC_PATH)%.c
	@mkdir -p $(dir $@)
	$(CC) -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) -c -o $@ $<
    
# Link
$(EXECUTABLE): $(OBJECTS)
	@mkdir -p $(dir $@)
	$(CC) -mmcu=$(MCU) -o $@ $^ $(LDFLAGS)

ifneq ($(MAKECMDGOALS), clean)
  -include $(DEPEND)
endif

clean:
	@rm -r -f $(BUILD_PATH) $(EXECUTABLE)
