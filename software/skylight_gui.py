#!/usr/bin/env python3

import py_modules.python_modules.tk_extensions as tkext
#tkext.ExceptionHandler.install()

import os
import sys
import json
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from py_modules.python_modules.app import App
import py_modules.python_modules.encodable_class as ec

from py_modules.skylight.gui_Transitions import EditTransitionList
from py_modules.skylight.gui_LightingAlarms import EditLightingAlarmList
from py_modules.skylight.gui_Modesets import EditModesetAlarmList
from py_modules.skylight.gui_Colors import EditColor
from py_modules.skylight.gui_Terminal import Terminal
from py_modules.skylight.colors import Color_raw
import py_modules.skylight.settings as settings
import py_modules.skylight.btLink as btLink
import py_modules.skylight.gui_btLink as gui_btLink

#---------------------------------------------------------------------------------------------------
class skylight_gui(App):
    def set_cmdline_args(self, parser):
        App.set_cmdline_args(self, parser)
        parser.description = "Skylight LED Firmware Loader"
        
    def main(self):
        App.main(self)
        
        if(os.path.exists("settings.json")):
            settings.S_DATA = settings.Skylight_Settings.from_json("settings.json")
        else:
            # create default settings
            settings.S_DATA = settings.Skylight_Settings()
        
        self.color = Color_raw(0,0,0,0)
        
        # Run GUI
        self.gui_main()
        
        settings.S_DATA.save_json("settings.json")
        
    def gui_main(self):
        self.tkWindow = tk.Tk()
        self.tkWindow.title("Skylight GUI")
        fr_main = ttk.Frame(self.tkWindow, padding = 5)
        fr_main.pack()
        
        #--------------------------------------------------------
        fr_bluetooth = ttk.LabelFrame(fr_main, text="Bluetooth")
        fr_bluetooth.pack(expand=True, padx=5, pady=5, fill=tk.X)
        self.pb_tgl_connect = ttk.Button(
            fr_bluetooth,
            text="Connect",
            command=self.pb_tgl_connect_click
        )
        self.pb_tgl_connect.pack(fill=tk.X)
        
        #--------------------------------------------------------
        fr_config = ttk.LabelFrame(fr_main, text="Configuration")
        fr_config.pack(expand=True, padx=5, pady=5, fill=tk.X)
        
        ttk.Button(
            fr_config,
            text="Edit Transitions",
            command=self.pb_edit_transitions
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_config,
            text="Edit Modeset Change Alarms",
            command=self.pb_edit_modeset_alarms
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_config,
            text="Edit Lighting Alarms",
            command=self.pb_edit_lighting_alarms
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_config,
            text="Send Config!",
            command=self.pb_send_cfg
        ).pack(fill=tk.X)
        
        #--------------------------------------------------------
        fr_clock = ttk.LabelFrame(fr_main, text="Clock")
        fr_clock.pack(expand=True, padx=5, pady=5, fill=tk.X)
        ttk.Button(
            fr_clock,
            text="Sync Date/Time",
            command=self.pb_sync_datetime
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_clock,
            text="Update Clock Correction",
            command=self.pb_update_clk_correction
        ).pack(fill=tk.X)
        
        #--------------------------------------------------------
        fr_debug = ttk.LabelFrame(fr_main, text="Debug")
        fr_debug.pack(expand=True, padx=5, pady=5, fill=tk.X)
        ttk.Button(
            fr_debug,
            text="Set Color",
            command=self.pb_set_color
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_debug,
            text="Terminal",
            command=self.pb_terminal
        ).pack(fill=tk.X)
        
        self.fr = fr_main
        
        # block until the window exits
        self.tkWindow.wait_window(self.tkWindow)
        
    def pb_edit_transitions(self):
        dlg = EditTransitionList(
            self.fr,
            settings.S_DATA.t_list
        )
        
    def pb_edit_modeset_alarms(self):
        dlg = EditModesetAlarmList(
            self.fr,
            settings.S_DATA.cfg.modeset_change_table.alarms
        )
        
        # Set the default modeset to the first one
        if(len(settings.S_DATA.cfg.modeset_change_table.alarms) != 0):
            settings.S_DATA.cfg.default_modeset = settings.S_DATA.cfg.modeset_change_table.alarms[0].data
        
    def pb_edit_lighting_alarms(self):
        dlg = EditLightingAlarmList(
            self.fr,
            settings.S_DATA.cfg.lighting_alarm_table.alarms
        )
        
    def pb_send_cfg(self):
        image = settings.S_DATA.cfg.compile()
        if(gui_btLink.check_bt_connected()):
            settings.BT_LINK.set_time()
            settings.BT_LINK.send_config(image)
            
    def pb_sync_datetime(self):
        image = settings.S_DATA.cfg.compile()
        if(gui_btLink.check_bt_connected()):
            settings.BT_LINK.set_time()
            
    def pb_set_color(self):
        dlg = EditColor(self.fr, self.color)
        if(dlg.result):
            self.color = dlg.C
            if(gui_btLink.check_bt_connected()):
                settings.BT_LINK.set_rgbw(self.color)

    def pb_terminal(self):
        if(gui_btLink.check_bt_connected()):
            Terminal(self.fr, settings.BT_LINK)
            
    def pb_update_clk_correction(self):
        if(gui_btLink.check_bt_connected()):
            # Query hardware
            ref_time = settings.BT_LINK.get_ref_time()
            corrected_minutes = settings.BT_LINK.get_ttl_clk_correct()
            
            actual_time = datetime.datetime.now()
            hw_time = settings.BT_LINK.get_time()
            
            if(hw_time == None):
                messagebox.showerror(
                    title = "Error!",
                    message = "Time was not set. Cannot calculate clock correction."
                )
                return
            
            # Undo hardware clock correction
            hw_time -= datetime.timedelta(minutes=corrected_minutes)
            
            elapsed = (actual_time - ref_time).total_seconds()
            delta = (actual_time - hw_time).total_seconds()
            self.log.info("Clock drift: %d seconds", delta)
            self.log.info("Time elapsed: %d seconds", elapsed)
            if(delta < 60):
                messagebox.showinfo(
                    title = "Info",
                    message = "Hardware clock drift is less than 60 seconds. Not updating correction."
                )
                return
                
            # Hardware time is subject to rounding to nearest second.
            # Calculate both ends of the possible interval
            correction_interval_L = elapsed / delta
            correction_interval_H = elapsed / (delta-1)
            
            # Calculate the error margin of the correction, and the original clock error
            correction_error = abs(
                (correction_interval_H - correction_interval_L) 
                / ((correction_interval_H + correction_interval_L)/2)
            )
            clock_error = abs(delta / elapsed)
            
            # Only implement a new clock correction value if the new correction has a better confidence
            # level.
            self.log.info("Current clock error: %.4f%%" % clock_error)
            self.log.info("Error of calculated correction: %.4f%%" % correction_error)
            if(correction_error > clock_error):
                messagebox.showinfo(
                    title = "Info",
                    message = "Not enough confidence in new correction value. Not updating correction."
                )
                return
            
            # Looks good. Pick midpoint of correction range
            settings.S_DATA.cfg.clock_correction_interval = round((correction_interval_H + correction_interval_L) / 2)
            
            messagebox.showinfo(
                title = "Info",
                message = "Updated clock correction interval. Re-send configuration to apply."
            )
            
            
    def pb_tgl_connect_click(self):
        
        if((settings.BT_LINK == None) or (settings.BT_LINK.connected == False)):
            # Connect
            
            if(gui_btLink.check_bt_addr()):
                
                if(settings.BT_LINK == None):
                    settings.BT_LINK = btLink.btLink(settings.S_DATA.bt_addr)
                
                try:
                    settings.BT_LINK.open()
                except:
                    print("BT connect error")
                    settings.BT_LINK = None
                    return
                
                self.pb_tgl_connect.configure(text="Disconnect")
        else:
            # Disconnect
            settings.BT_LINK.close()
            
            self.pb_tgl_connect.configure(text="Connect")
    
####################################################################################################
if __name__ == '__main__':
    A = skylight_gui()
    A.main()
