
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ..python_modules import tk_extensions as tkext
from . import eeprom_config as eecfg

#---------------------------------------------------------------------------------------------------
class EditModePair(tkext.Dialog):
    def __init__(self, parent, M, T_list = []):
        self.M = M
        self.T_list = T_list
        
        self.T_names = []
        for T in self.T_list:
            name = "%s::%s" % (type(T).__name__, T.name)
            self.T_names.append(name)
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Edit Mode Pair")
        
    def create_body(self, master_fr):
        # Construct the contents of the dialog
                
        # Transition Selectors
        ttk.Label(master_fr, text="On Transition:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.cmb_on_transition = ttk.Combobox(
            master_fr,
            state= 'readonly',
            values=self.T_names
        )
        self.cmb_on_transition.grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        ttk.Label(master_fr, text="Off Transition:").grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.cmb_off_transition = ttk.Combobox(
            master_fr,
            state= 'readonly',
            values=self.T_names
        )
        self.cmb_off_transition.grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        master_fr.columnconfigure(1, weight=1)
        master_fr.columnconfigure(tk.ALL, pad=5)
        master_fr.rowconfigure(tk.ALL, pad=5)
        
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        if(self.M):
            for i,v in enumerate(self.T_list):
                if(self.M[0] is v):
                    self.cmb_on_transition.current(i)
                    break
            
            for i,v in enumerate(self.T_list):
                if(self.M[1] is v):
                    self.cmb_off_transition.current(i)
                    break
        
    def dlg_validate(self):
        
        #---------------
        # Validate Transitions
        #---------------
        i = self.cmb_on_transition.current()
        if(i < 0):
            messagebox.showerror(
                title = "Error!",
                message = "Must select an 'On' transition."
            )
            return(False)
            
        i = self.cmb_off_transition.current()
        if(i < 0):
            messagebox.showerror(
                title = "Error!",
                message = "Must select an 'Off' transition."
            )
            return(False)
        
        return(True)
    
    def dlg_apply(self):
        i_on = self.cmb_on_transition.current()
        i_off = self.cmb_off_transition.current()
        self.M = (self.T_list[i_on], self.T_list[i_off])
        
#---------------------------------------------------------------------------------------------------
class EditModesetAlarm(tkext.ListEdit):
    def __init__(self, parent, MA, MA_list = [], T_list = []):
        
        self.MA = MA
        self.MA_list = MA_list
        self.T_list = T_list
        
        tkext.ListEdit.__init__(self, parent = parent, title = "Edit Modeset Alarm", item_list = MA.data.modes.copy())
        
    def get_item_label(self, I, idx):
        return("%d: %s::%s, %s::%s" % (idx+1,
                                       type(I[0]).__name__, I[0].name,
                                       type(I[1]).__name__, I[1].name
                                      ))
    
    def new_item(self):
        # Create new mode pair
        
        # Open edit dialog
        dlg = EditModePair(self.tkWindow, None, self.T_list)
        if(dlg.result):
            return(dlg.M)
        else:
            return(None)
    
    def edit_item(self, I):
        dlg = EditModePair(self.tkWindow, I, self.T_list)
        if(dlg.result):
            return(dlg.M)
        else:
            return(None)
        
    # Force redraw all so that numbers are correct when changing
    def on_pb_Up(self):
        tkext.ListEdit.on_pb_Up(self)
        self.refresh_modeset_list()
    def on_pb_Down(self):
        tkext.ListEdit.on_pb_Down(self)
        self.refresh_modeset_list()
    def on_pb_Delete(self):
        tkext.ListEdit.on_pb_Delete(self)
        self.refresh_modeset_list()
    def refresh_modeset_list(self):
        selidx = self.lb_items.curselection()
        if(len(selidx) == 0):
            selidx = None
        else:
            selidx = int(selidx[0])
        
        for idx,I in enumerate(self.item_list):
            self.lb_items.delete(idx)
            self.lb_items.insert(idx, self.get_item_label(I, idx))
        
        if(selidx != None):
            self.lb_items.selection_set(selidx)
    
    def create_body(self, master_fr):
        # Construct the contents of the dialog
        
        fr_alarm = ttk.LabelFrame(master_fr, text="Alarm Settings")
        fr_alarm.pack(side=tk.LEFT, fill = tk.BOTH, padx=5, pady=5)
        fr_item_list = ttk.LabelFrame(master_fr, text="Mode Set")
        fr_item_list.pack(side=tk.RIGHT, fill = tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the list editor too
        tkext.ListEdit.create_body(self, fr_item_list)
        
        # Name
        ttk.Label(fr_alarm, text="Name:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.txt_name_var = tk.StringVar(self.tkWindow)
        ttk.Entry(fr_alarm, textvariable = self.txt_name_var).grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        # Hour
        ttk.Label(fr_alarm, text="Alarm Hour:").grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.sb_hour_var = tk.IntVar(self.tkWindow)
        tk.Spinbox(
            fr_alarm,
            from_=0,
            to=23,
            increment=1,
            textvariable=self.sb_hour_var
        ).grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        # Minute
        ttk.Label(fr_alarm, text="Alarm Minute:").grid(row=2, column=0, sticky=(tk.N, tk.E))
        self.sb_minute_var = tk.IntVar(self.tkWindow)
        tk.Spinbox(
            fr_alarm,
            from_=0,
            to=59,
            increment=1,
            textvariable=self.sb_minute_var
        ).grid(row=2, column=1, sticky=(tk.E, tk.W))
        
        # Day of week checkboxes
        ttk.Label(fr_alarm, text="Days of the week:").grid(row=3, column=0, sticky=(tk.N, tk.E))
        fr_dow_boxes = ttk.Frame(fr_alarm)
        fr_dow_boxes.grid(row=3, column=1, sticky=(tk.E, tk.W))
        dows = ["Su","M", "T", "W", "R", "F", "Sa"]
        self.cb_dow_vars = []
        for i, dow in enumerate(dows):
            v = tk.IntVar(self.tkWindow)
            cb = tk.Checkbutton(fr_dow_boxes, text=dow, variable=v)
            cb.pack(side=tk.LEFT)
            self.cb_dow_vars.append(v)
        
        fr_alarm.columnconfigure(1, weight=1)
        fr_alarm.columnconfigure(tk.ALL, pad=5)
        fr_alarm.rowconfigure(tk.ALL, pad=5)
        
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        tkext.ListEdit.dlg_initialize(self)
        self.txt_name_var.set(self.MA.name)
        self.sb_hour_var.set(self.MA.hour)
        self.sb_minute_var.set(self.MA.minute)
        for i,v in enumerate(self.cb_dow_vars):
            if(i in self.MA.dow_list):
                v.set(1)
        
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
        for other_MA in self.MA_list:
            if(self.MA is other_MA):
                continue # skip self
            if(name == other_MA.name):
                messagebox.showerror(
                    title = "Error!",
                    message = "Another alarm already has the same name."
                )
                return(False)
        
        #---------------
        # Validate hour/minute
        #---------------
        if((self.sb_hour_var.get() < 0) or (self.sb_hour_var.get() > 23)):
            messagebox.showerror(
                title = "Error!",
                message = "Hour must be between 0-23."
            )
            return(False)
            
        if((self.sb_minute_var.get() < 0) or (self.sb_minute_var.get() > 59)):
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
        # Validate Modesets
        #---------------
        if(len(self.item_list) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "Must have at least one mode pair"
            )
            return(False)
        
        return(True)
    
    def dlg_apply(self):
        self.MA.name = self.txt_name_var.get().strip()
        self.MA.hour = self.sb_hour_var.get()
        self.MA.minute = self.sb_minute_var.get()
        self.MA.dow_list = []
        for i,v in enumerate(self.cb_dow_vars):
            if(v.get()):
               self.MA.dow_list.append(i)
        
        self.MA.data.modes = self.item_list
        
#---------------------------------------------------------------------------------------------------
class EditModesetAlarmList(tkext.ListEdit):
    def __init__(self, parent, MA_list = [], T_list = []):
        
        self.T_list = T_list
        
        tkext.ListEdit.__init__(self, parent = parent, title = "Edit Modeset Alarms", item_list = MA_list)
        
    def get_item_label(self, I, idx):
        return(I.name)
    
    def new_item(self):
        # Create lighting alarm item
        MA = eecfg.AlarmEntry()
        MA.name = "New Alarm"
        MA.data = eecfg.ModeSet()
        
        # Open edit dialog
        dlg = EditModesetAlarm(self.tkWindow, MA, self.item_list, self.T_list)
        if(dlg.result):
            return(dlg.MA)
        else:
            return(None)
    
    def edit_item(self, I):
        dlg = EditModesetAlarm(self.tkWindow, I, self.item_list, self.T_list)
        if(dlg.result):
            return(dlg.MA)
        else:
            return(None)
