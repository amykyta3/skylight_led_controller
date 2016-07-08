
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ..python_modules import tk_extensions as tkext
from . import eeprom_config as eecfg
from . import colors
from . import btLink
from . import gui_btLink
from . import settings

#---------------------------------------------------------------------------------------------------
class EditColor(tkext.Dialog):
    def __init__(self, parent, C):
        self.C = C
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Edit Color")
        
    #---------------------------------------------------------------
    def create_buttonbox(self, master_fr):
        tkext.Dialog.create_buttonbox(self, master_fr)
        
        ttk.Button(
            master_fr,
            text="Test",
            command=self.pb_Test
        ).pack(side=tk.LEFT)
        
    #---------------------------------------------------------------
    def create_body(self, master_fr):
        # Construct the contents of the dialog
        
        # Variable transformation functions
        def var_int2hex(var_in, var_out):
            n = int(var_in.get())
            var_out.set("0x%04X" % n)
        def update_slider(v, var):
            try:
                v = int(v,0)
                var.set(v)
                return(True)
            except:
                return(False)
        
        # Color Sliders
        self.R_var = tk.DoubleVar(self.tkWindow)
        R_str_var = tk.StringVar(self.tkWindow)
        ttk.Label(master_fr, text="R:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        ttk.Scale(
            master_fr,
            from_=0, to=0xFFFF,
            variable = self.R_var
        ).grid(row=0, column=1, sticky=(tk.E, tk.W))
        ttk.Entry(
            master_fr,
            textvariable= R_str_var,
            validate= "focusout",
            validatecommand= (self.tkWindow.register(lambda v: update_slider(v, self.R_var)), '%P')
        ).grid(row=0, column=2, sticky=(tk.E, tk.W))
        self.R_var.trace("w", lambda *args: var_int2hex(self.R_var, R_str_var))
        
        self.G_var = tk.DoubleVar(self.tkWindow)
        G_str_var = tk.StringVar(self.tkWindow)
        ttk.Label(master_fr, text="G:").grid(row=1, column=0, sticky=(tk.N, tk.E))
        ttk.Scale(
            master_fr,
            from_=0, to=0xFFFF,
            variable = self.G_var
        ).grid(row=1, column=1, sticky=(tk.E, tk.W))
        ttk.Entry(
            master_fr,
            textvariable= G_str_var,
            validate= "focusout",
            validatecommand= (self.tkWindow.register(lambda v: update_slider(v, self.G_var)), '%P')
        ).grid(row=1, column=2, sticky=(tk.E, tk.W))
        self.G_var.trace("w", lambda *args: var_int2hex(self.G_var, G_str_var))
        
        self.B_var = tk.DoubleVar(self.tkWindow)
        B_str_var = tk.StringVar(self.tkWindow)
        ttk.Label(master_fr, text="B:").grid(row=2, column=0, sticky=(tk.N, tk.E))
        ttk.Scale(
            master_fr,
            from_=0, to=0xFFFF,
            variable = self.B_var
        ).grid(row=2, column=1, sticky=(tk.E, tk.W))
        ttk.Entry(
            master_fr,
            textvariable= B_str_var,
            validate= "focusout",
            validatecommand= (self.tkWindow.register(lambda v: update_slider(v, self.B_var)), '%P')
        ).grid(row=2, column=2, sticky=(tk.E, tk.W))
        self.B_var.trace("w", lambda *args: var_int2hex(self.B_var, B_str_var))
        
        self.W_var = tk.DoubleVar(self.tkWindow)
        W_str_var = tk.StringVar(self.tkWindow)
        ttk.Label(master_fr, text="W:").grid(row=3, column=0, sticky=(tk.N, tk.E))
        ttk.Scale(
            master_fr,
            from_=0, to=0xFFFF,
            variable = self.W_var
        ).grid(row=3, column=1, sticky=(tk.E, tk.W))
        ttk.Entry(
            master_fr,
            textvariable= W_str_var,
            validate= "focusout",
            validatecommand= (self.tkWindow.register(lambda v: update_slider(v, self.W_var)), '%P')
        ).grid(row=3, column=2, sticky=(tk.E, tk.W))
        self.W_var.trace("w", lambda *args: var_int2hex(self.W_var, W_str_var))
        
        master_fr.columnconfigure(1, weight=1)
        master_fr.columnconfigure(tk.ALL, pad=5)
        master_fr.rowconfigure(tk.ALL, pad=5)
        
    #---------------------------------------------------------------
    def pb_Test(self, event=None):
        C = colors.Color_raw(
            int(self.R_var.get()),
            int(self.G_var.get()),
            int(self.B_var.get()),
            int(self.W_var.get())
        )
        
        if(gui_btLink.check_bt_addr()):
            with btLink.btLink(settings.S_DATA.bt_addr) as S:
                S.set_rgbw(C)
    
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        if(self.C and issubclass(type(self.C), colors.Color)):
            #++ Initialize sliders to color value
            r,g,b,w = self.C.get_rgbw()
            self.R_var.set(r)
            self.G_var.set(g)
            self.B_var.set(b)
            self.W_var.set(w)
        else:
            self.R_var.set(0)
            self.G_var.set(0)
            self.B_var.set(0)
            self.W_var.set(0)
        
    def dlg_validate(self):
        return(True)
    
    def dlg_apply(self):
        self.C = colors.Color_raw(
            int(self.R_var.get()),
            int(self.G_var.get()),
            int(self.B_var.get()),
            int(self.W_var.get())
        )
        