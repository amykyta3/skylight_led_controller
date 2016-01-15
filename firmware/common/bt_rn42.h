
#ifndef BT_RN42_H
#define BT_RN42_H

#include <stdint.h>

//--------------------------------------------------------------------------------------------------
/**
 * \brief Enter command mode
 * \retval 0 OK!
 * \retval 1 Failed
**/
uint8_t bt_enter_cmd_mode(void);

//--------------------------------------------------------------------------------------------------
/**
 * \brief Exit RN42 Command mode
**/
void bt_exit_cmd_mode(void);

//--------------------------------------------------------------------------------------------------
/**
 * \brief Send soft-reset command to RN42
**/
void bt_reboot(void);

//--------------------------------------------------------------------------------------------------
/**
 * \brief Send a SET command to RN42
 * 
 * For any command that expects an "AOK" response.
 * Command includes trailing \\r
 * 
 * \param cmd       Command string
 * \retval 0 OK!
 * \retval 1 Failed
 **/
uint8_t bt_S_cmd(const char *cmd);


#endif
