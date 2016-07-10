#!/usr/bin/env python3

import py_modules.python_modules.tk_extensions as tkext
#tkext.ExceptionHandler.install()

import os
import sys
import json
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
        
        ttk.Button(
            fr_main,
            text="Edit Transitions",
            command=self.pb_edit_transitions
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
            text="Edit Modeset Change Alarms",
            command=self.pb_edit_modeset_alarms
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
            text="Edit Lighting Alarms",
            command=self.pb_edit_lighting_alarms
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
            text="Send Config!",
            command=self.pb_send_cfg
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
            text="Sync Date/Time",
            command=self.pb_sync_datetime
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
            text="Set Color",
            command=self.pb_set_color
        ).pack(fill=tk.X)
        
        ttk.Button(
            fr_main,
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
        
    def pb_edit_lighting_alarms(self):
        dlg = EditLightingAlarmList(
            self.fr,
            settings.S_DATA.cfg.lighting_alarm_table.alarms
        )
        
    def pb_send_cfg(self):
        image = settings.S_DATA.cfg.compile()
        if(gui_btLink.check_bt_addr()):
            with btLink.btLink(settings.S_DATA.bt_addr) as S:
                S.set_time()
                S.send_config(image)
            
    def pb_sync_datetime(self):
        image = settings.S_DATA.cfg.compile()
        if(gui_btLink.check_bt_addr()):
            with btLink.btLink(settings.S_DATA.bt_addr) as S:
                S.set_time()
            
    def pb_set_color(self):
        dlg = EditColor(self.fr, self.color)
        if(dlg.result):
            self.color = dlg.C
            if(gui_btLink.check_bt_addr()):
                with btLink.btLink(settings.S_DATA.bt_addr) as S:
                    S.set_rgbw(self.color)

    def pb_terminal(self):
        if(gui_btLink.check_bt_addr()):
            with btLink.btLink(settings.S_DATA.bt_addr) as S:
                Terminal(self.fr, S)
        
####################################################################################################
if __name__ == '__main__':
    A = skylight_gui()
    A.main()
