#!/usr/bin/env python3

import py_modules.python_modules.tk_extensions as tkext
#tkext.ExceptionHandler.install()

import os
import sys
import json
import datetime
import tkinter as tk
from tkinter import ttk

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
        
        ttk.Button(
            fr_debug,
            text="test",
            command=self.pb_TEST
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
            
    def pb_TEST(self):
        if(gui_btLink.check_bt_connected()):
            ref_time = settings.BT_LINK.get_ref_time()
            hw_time = settings.BT_LINK.get_time()
            actual_time = datetime.datetime.now()
            
            print("HW Time    ", hw_time)
            print("Actual Time", actual_time)
            print("elapsed", actual_time - ref_time)
            
            elapsed = (actual_time - ref_time).total_seconds()
            delta = (actual_time - hw_time).total_seconds()
            correction_interval = elapsed / delta
            print("Correction interval", correction_interval)
            
            
                
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
