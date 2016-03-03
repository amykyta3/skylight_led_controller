
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ..python_modules import tk_extensions as tkext
from . import eeprom_config as eecfg

#---------------------------------------------------------------------------------------------------
class Edit_LightingAlarm(tkext.Dialog):
    def __init__(self, parent, LA, LA_list = [], T_list = []):
        """
        LA: Lighting Alarm to edit
        T_list: List of other existing transitions
        """
        self.LA = LA
        self.LA_list = LA_list
        self.T_list = T_list
        
        self.T_names = []
        for T in self.T_list:
            name = "%s::%s" % (type(T).__name__, T.name)
            self.T_names.append(name)
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Edit Lighting Alarm")
        
    def create_body(self, master_fr):
        # Construct the contents of the dialog
                
        # Name
        ttk.Label(master_fr, text="Name:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.txt_name_var = tk.StringVar(self.tkWindow)
        ttk.Entry(master_fr, textvariable = self.txt_name_var).grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        # Hour
        ttk.Label(master_fr, text="Alarm Hour:").grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.sb_hour_var = tk.IntVar(self.tkWindow)
        tk.Spinbox(
            master_fr,
            from_=0,
            to=23,
            increment=1,
            textvariable=self.sb_hour_var
        ).grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        # Minute
        ttk.Label(master_fr, text="Alarm Minute:").grid(row=2, column=0, sticky=(tk.N, tk.E))
        self.sb_minute_var = tk.IntVar(self.tkWindow)
        tk.Spinbox(
            master_fr,
            from_=0,
            to=59,
            increment=1,
            textvariable=self.sb_minute_var
        ).grid(row=2, column=1, sticky=(tk.E, tk.W))
        
        # Day of week checkboxes
        ttk.Label(master_fr, text="Days of the week:").grid(row=3, column=0, sticky=(tk.N, tk.E))
        fr_dow_boxes = ttk.Frame(master_fr)
        fr_dow_boxes.grid(row=3, column=1, sticky=(tk.E, tk.W))
        dows = ["Su","M", "T", "W", "R", "F", "Sa"]
        self.cb_dow_vars = []
        for i, dow in enumerate(dows):
            v = tk.IntVar(self.tkWindow)
            cb = tk.Checkbutton(fr_dow_boxes, text=dow, variable=v)
            cb.pack(side=tk.LEFT)
            self.cb_dow_vars.append(v)
        
        # Transition Selector
        ttk.Label(master_fr, text="Transition:").grid(row=4, column=0, sticky=(tk.N, tk.E))
        self.combo_transition = ttk.Combobox(
            master_fr,
            state= 'readonly',
            values=self.T_names
        )
        self.combo_transition.grid(row=4, column=1, sticky=(tk.E, tk.W))
        
        master_fr.columnconfigure(1, weight=1)
        master_fr.columnconfigure(tk.ALL, pad=5)
        master_fr.rowconfigure(tk.ALL, pad=5)
        
        
        
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        self.txt_name_var.set(self.LA.name)
        self.sb_hour_var.set(self.LA.hour)
        self.sb_minute_var.set(self.LA.minute)
        for i,v in enumerate(self.cb_dow_vars):
            if(i in self.LA.dow_list):
                v.set(1)
        
        for i,v in enumerate(self.T_list):
            if(self.LA.data is v):
                self.combo_transition.current(i)
                break
        
    def dlg_validate(self):
        
        #---------------
        # Validate name
        #---------------
        name = self.txt_name_var.get().strip()
        
        # check if name is acceptable
        if(len(name) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "Name cannot be empty."
            )
            return(False)
            
        # check if any other transitions have the same name
        for other_LA in self.LA_list:
            if(self.LA is other_LA):
                continue # skip self
            if(name == other_LA.name):
                messagebox.showerror(
                    title = "Error!",
                    message = "Another alarm already has the same name."
                )
                return(False)
        
        #---------------
        # Validate hour/minute
        #---------------
        if((self.sb_hour_var.get() < 0) or (self.sb_hour_var.get() >= 23)):
            messagebox.showerror(
                title = "Error!",
                message = "Hour must be between 0-23."
            )
            return(False)
            
        if((self.sb_minute_var.get() < 0) or (self.sb_minute_var.get() >= 60)):
            messagebox.showerror(
                title = "Error!",
                message = "Minute must be between 0-59."
            )
            return(False)
        
        #---------------
        # Validate DOW
        #---------------
        dows = []
        for i,v in enumerate(self.cb_dow_vars):
            if(v.get()):
               dows.append(i) 
        if(len(dows) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "Check at least one day of the week."
            )
            return(False)
        
        #---------------
        # Validate Transition
        #---------------
        i = self.combo_transition.current()
        if(i < 0):
            messagebox.showerror(
                title = "Error!",
                message = "Must select a transition."
            )
            return(False)
        
        return(True)
    
    def dlg_apply(self):
        self.LA.name = self.txt_name_var.get().strip()
        self.LA.hour = self.sb_hour_var.get()
        self.LA.minute = self.sb_minute_var.get()
        self.LA.dow_list = []
        for i,v in enumerate(self.cb_dow_vars):
            if(v.get()):
               self.LA.dow_list.append(i)
        
        i = self.combo_transition.current()
        self.LA.data = self.T_list[i]
        
class EditLightingAlarmList(tkext.ListEdit):
    def __init__(self, parent, LA_list = [], T_list = []):
        
        self.T_list = T_list
        
        tkext.ListEdit.__init__(self, parent = parent, title = "Edit Lighting Alarms", item_list = LA_list)
        
    def get_item_label(self, I):
        return(I.name)
    
    def new_item(self):
        # Create lighting alarm item
        LA = eecfg.AlarmEntry()
        LA.name = "New Alarm"
        
        # Open edit dialog
        dlg = Edit_LightingAlarm(self.tkWindow, LA, self.item_list, self.T_list)
        if(dlg.result):
            return(dlg.LA)
        else:
            return(None)
    
    def edit_item(self, I):
        dlg = Edit_LightingAlarm(self.tkWindow, I, self.item_list, self.T_list)
        if(dlg.result):
            return(dlg.LA)
        else:
            return(None)
