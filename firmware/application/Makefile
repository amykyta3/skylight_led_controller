########################################## Project Setup ###########################################

ECHO:=echo
CC:=avr-gcc
OBJCOPY:=avr-objcopy

PROJECT_NAME:=application
BUILD_PATH:=build/
COMMON_SRC_PATH:=../common/

MCU:=atxmega128d4
INCLUDES:= $(COMMON_SRC_PATH) $(COMMON_SRC_PATH)atxmega_modules/src/ config
CFLAGS:= -Os -Wall -std=gnu99 -ffunction-sections -fdata-sections -g
LDFLAGS:= -Wl,--gc-sections -Wl,-Map,$(BUILD_PATH)$(PROJECT_NAME).map -g
EXECUTABLE:= $(PROJECT_NAME).elf

SRC:= main.c
SRC+= cli_commands.c
SRC+= led_pwm.c
SRC+= eeprom_config.c
SRC+= debug.c
SRC+= light_switch.c
SRC+= led_transitions.c

COMMON_SRC:= bt_rn42.c
COMMON_SRC+= atxmega_modules/src/fifo.c
COMMON_SRC+= atxmega_modules/src/uart_io.c
COMMON_SRC+= atxmega_modules/src/cli.c
COMMON_SRC+= atxmega_modules/src/event_queue.c
COMMON_SRC+= atxmega_modules/src/rtc.c
COMMON_SRC+= atxmega_modules/src/string_ext.c

####################################################################################################

all:$(EXECUTABLE).hex

program:$(EXECUTABLE).hex
	../../software/firmware_loader.py -p /dev/rfcomm0 $<
	
dump_flash:
	avrdude -p x128d4 -c avrispmkII -U flash:r:flash.hex:i
	
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
	$(CC) -mmcu=$(MCU) -DBUILD_TIMESTAMP=$(shell date '+%s') -c -o $(BUILD_PATH)/timestamp.o timestamp.c
	
	$(CC) -mmcu=$(MCU) -o $@ $^ $(BUILD_PATH)/timestamp.o $(LDFLAGS)

# Intel-hex output
$(EXECUTABLE).hex: $(EXECUTABLE)
	$(OBJCOPY) -O ihex $< $@
	
ifneq ($(MAKECMDGOALS), clean)
  -include $(DEPEND)
endif

clean:
	@rm -r -f $(BUILD_PATH) $(EXECUTABLE) $(EXECUTABLE).hex
