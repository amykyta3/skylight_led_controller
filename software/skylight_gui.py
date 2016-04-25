#!/usr/bin/env python3

import py_modules.python_modules.tk_extensions as tkext
tkext.ExceptionHandler.install()

import os
import sys
import json
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

from py_modules.python_modules.app import App
import py_modules.python_modules.class_codec as class_codec

import py_modules.skylight as skylight

from py_modules.skylight.gui_Transitions import EditTransitionList
from py_modules.skylight.gui_LightingAlarms import EditLightingAlarmList
from py_modules.skylight.gui_Modesets import EditModesetAlarmList

#---------------------------------------------------------------------------------------------------
class skylight_gui(App):
    def set_cmdline_args(self, parser):
        App.set_cmdline_args(self, parser)
        parser.description = "Skylight LED Firmware Loader"
        
    def main(self):
        App.main(self)
        
        if(os.path.exists("settings.json")):
            self.Settings = skylight_settings.from_json("settings.json")
        else:
            # create default settings
            self.Settings = skylight_settings()
        
        self.color = (0,0,0)
        
        # Run GUI
        self.gui_main()
        
        self.Settings.save_json("settings.json")
        
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
        
        self.fr = fr_main
        
        # block until the window exits
        self.tkWindow.wait_window(self.tkWindow)
        
    def pb_edit_transitions(self):
        dlg = EditTransitionList(
            self.fr,
            self.Settings.t_list
        )
        
    def pb_edit_modeset_alarms(self):
        dlg = EditModesetAlarmList(
            self.fr,
            self.Settings.cfg.modeset_change_table.alarms,
            self.Settings.t_list
        )
        
    def pb_edit_lighting_alarms(self):
        dlg = EditLightingAlarmList(
            self.fr,
            self.Settings.cfg.lighting_alarm_table.alarms,
            self.Settings.t_list
        )
        
    def pb_send_cfg(self):
        image = self.Settings.cfg.compile()
        with skylight.btLink("/dev/rfcomm0") as S:
            S.set_time()
            S.send_config(image)
            
    def pb_sync_datetime(self):
        image = self.Settings.cfg.compile()
        with skylight.btLink("/dev/rfcomm0") as S:
            S.set_time()
            
    def pb_set_color(self):
        color = colorchooser.askcolor(initialcolor=self.color)[0]
        if(color):
            self.color = (int(color[0]), int(color[1]), int(color[2]))
            C = skylight.colors.Color_rgb(*self.color)
            with skylight.btLink("/dev/rfcomm0") as S:
                S.set_rgbw(C)
            

#---------------------------------------------------------------------------------------------------
class skylight_settings(class_codec.EncodableClass):
    encode_schema = {
        "cfg": skylight.eeConfig,
        "t_list": [skylight.eeprom_config.Transition]
    }
    
    def __init__(self):
        
        # Skylight configuration object
        self.cfg = skylight.eeConfig()
        
        # Pool of available transitions
        self.t_list = []
        
    @classmethod
    def from_json(cls, filename):
        with open(filename, 'r') as f:
            D = json.load(f)
        
        return(cls.from_dict(D))
        
    def save_json(self, filename):
        D = self.to_dict()
        with open(filename, 'w') as f:
            json.dump(D, f, indent=2, sort_keys = True)

####################################################################################################
if __name__ == '__main__':
    A = skylight_gui()
    A.main()
