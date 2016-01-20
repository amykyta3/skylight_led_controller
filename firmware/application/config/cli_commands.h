#ifndef CLI_COMMANDS_H
#define CLI_COMMANDS_H

#include <cli.h>
#include <stdint.h>

// If set to 1, command parsing recognizes multi-word arguments in quotes
#define PARSE_QUOTED_ARGS   0

// If set to 1, performs command lookup using a binary search instead of linear.
#define USE_BINARY_SEARCH   0

// maximum length of a command input line
#define CLI_STRBUF_SIZE    64

// Maximum number of arguments in a command (including command).
#define CLI_MAX_ARGC    8

// Table of commands: {"command_word" , function_name }
// Command words MUST be in alphabetical (ascii) order!! (A-Z then a-z) if using binary search
#define CMDTABLE    {"echo"  , cmd_echo     },\
                    {"id"    , cmd_id       },\
                    {"led"   , cmd_led      },\
                    {"reset" , cmd_reset    },\
                    {"rgbw"  , cmd_rgbw     }

// Custom command function prototypes:
int cmd_echo(uint8_t argc, char *argv[]);
int cmd_id(uint8_t argc, char *argv[]);
int cmd_led(uint8_t argc, char *argv[]);
int cmd_reset(uint8_t argc, char *argv[]);
int cmd_rgbw(uint8_t argc, char *argv[]);

#endif