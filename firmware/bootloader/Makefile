########################################## Project Setup ###########################################

ECHO:=echo
CC:=avr-gcc
OBJCOPY:=avr-objcopy

PROJECT_NAME:=bootloader
BUILD_PATH:=build/
COMMON_SRC_PATH:=../common/
MODULES_SRC_PATH:=atxmega_modules/src/

# Bootloader section byte address (NOT word address)
BOOTSTART:=0x20000

MCU:=atxmega128d4
INCLUDES:= $(COMMON_SRC_PATH) $(MODULES_SRC_PATH) config
CFLAGS:= -Os -Wall -std=c99 -ffunction-sections -fdata-sections
LDFLAGS:= -Wl,--gc-sections,--section-start=.text=$(BOOTSTART) -Wl,-Map,$(BUILD_PATH)$(PROJECT_NAME).map
EXECUTABLE:= $(PROJECT_NAME).elf

SRC:= main.c
SRC+= cli_commands.c
SRC+= $(MODULES_SRC_PATH)/fifo.c
SRC+= $(MODULES_SRC_PATH)/uart_io.c
SRC+= $(MODULES_SRC_PATH)/cli.c

COMMON_SRC:= init0.c

####################################################################################################

all:$(EXECUTABLE)

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
	@$(CC) -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) -c -o $@ $<
	
$(COMMON_BUILD_PATH)%.o: $(COMMON_SRC_PATH)%.c
	@mkdir -p $(dir $@)
	@$(CC) -mmcu=$(MCU) $(addprefix -I,$(INCLUDES)) $(CFLAGS) -c -o $@ $<
    
# Link
$(EXECUTABLE): $(OBJECTS)
	@mkdir -p $(dir $@)
	@$(CC) -mmcu=$(MCU) -o $@ $^ $(LDFLAGS)

ifneq ($(MAKECMDGOALS), clean)
  -include $(DEPEND)
endif

clean:
	@rm -r -f $(BUILD_PATH) $(EXECUTABLE)
