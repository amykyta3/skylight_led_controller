
import tkinter as tk
from tkinter import ttk
from tkinter import tix
from tkinter import colorchooser
from tkinter import messagebox

from ..python_modules import tk_extensions as tkext
from . import eeprom_config as eecfg
from . import colors

#---------------------------------------------------------------------------------------------------
class Edit_trans_Immediate(tkext.Dialog):
    def __init__(self, parent, T, T_list = []):
        """
        T: Transition to edit
        T_list: List of other existing transitions
        """
        self.T = T
        self.T_list = T_list
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Edit Immediate Transition")
        
    def create_body(self, master_fr):
        # Construct the contents of the dialog
        
        # Name
        ttk.Label(master_fr, text="Name:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.txt_name = ttk.Entry(
            master_fr
        )
        self.txt_name.grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        # Delay
        ttk.Label(master_fr, text="Delay (seconds):").grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.sb_delay = tk.Spinbox(
            master_fr,
            from_=0.0,
            to=2400.0,
            increment=1.0
        )
        self.sb_delay.grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        # Color Chooser
        ttk.Label(master_fr, text="Color:").grid(row=2, column=0, sticky=(tk.N, tk.E))
        self.pb_color = tk.Button(
            master_fr,
            command=self.on_pb_color
        )
        self.pb_color.grid(row=2, column=1, sticky=(tk.E, tk.W))
        
        master_fr.columnconfigure(1, weight=1)
        master_fr.columnconfigure(tk.ALL, pad=5)
        master_fr.rowconfigure(tk.ALL, pad=5)
    
    #---------------------------------------------------------------
    # Button actions
    #---------------------------------------------------------------
    def on_pb_color(self):
        color = colorchooser.askcolor(initialcolor=self.color)[0]
        if(color):
            self.color = (int(color[0]), int(color[1]), int(color[2]))
            self.pb_color.configure(bg="#%02X%02X%02X" % self.color)
        
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        
        # Name
        self.txt_name.delete(0,tk.END)
        self.txt_name.insert(tk.END, self.T.name)
        
        # Delay
        self.sb_delay.delete(0,tk.END)
        self.sb_delay.insert(tk.END, self.T.delay)
        
        # Color Chooser
        if(type(self.T.color) != colors.Color_rgb):
            raise TypeError("TODO: Support different color encodings")
        
        r = int(self.T.color.r * 255.0)
        g = int(self.T.color.g * 255.0)
        b = int(self.T.color.b * 255.0)
        self.color = (r,g,b)
        self.pb_color.configure(bg="#%02X%02X%02X" % self.color)
        
    def dlg_validate(self):
        
        #---------------
        # Validate name
        #---------------
        name = self.txt_name.get().strip()
        
        # check if name is acceptable
        if(len(name) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "Name cannot be empty."
            )
            return(False)
            
        # check if any other transitions have the same name
        for other_T in self.T_list:
            if(self.T is other_T):
                continue # skip self
            if(name == other_T.name):
                messagebox.showerror(
                    title = "Error!",
                    message = "Another transition already has the same name."
                )
                return(False)
        
        return(True)
    
    def dlg_apply(self):
        self.T.name = self.txt_name.get()
        self.T.delay = float(self.sb_delay.get())
        self.T.color = colors.Color_rgb(*self.color)
    
#---------------------------------------------------------------------------------------------------
class Edit_trans_Fade(tkext.Dialog):
    def __init__(self, parent, T, T_list = []):
        """
        T: Transition to edit
        T_list: List of other existing transitions
        """
        self.T = T
        self.T_list = T_list
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Edit Fade Transition")
        
    def create_body(self, master_fr):
        # Construct the contents of the dialog
        
        # Name
        ttk.Label(master_fr, text="Name:").grid(row=0, column=0, sticky=(tk.N, tk.E))
        self.txt_name = ttk.Entry(
            master_fr
        )
        self.txt_name.grid(row=0, column=1, sticky=(tk.E, tk.W))
        
        # Delay
        ttk.Label(master_fr, text="Delay (seconds):").grid(row=1, column=0, sticky=(tk.N, tk.E))
        self.sb_delay = tk.Spinbox(
            master_fr,
            from_=0.0,
            to=2400.0,
            increment=1.0
        )
        self.sb_delay.grid(row=1, column=1, sticky=(tk.E, tk.W))
        
        # Duration
        ttk.Label(master_fr, text="Duration (seconds):").grid(row=2, column=0, sticky=(tk.N, tk.E))
        self.sb_duration = tk.Spinbox(
            master_fr,
            from_=0.0,
            to=2400.0,
            increment=1.0
        )
        self.sb_duration.grid(row=2, column=1, sticky=(tk.E, tk.W))
        
        # Color Chooser
        ttk.Label(master_fr, text="Color:").grid(row=3, column=0, sticky=(tk.N, tk.E))
        self.pb_color = tk.Button(
            master_fr,
            command=self.on_pb_color
        )
        self.pb_color.grid(row=3, column=1, sticky=(tk.E, tk.W))
        
        master_fr.columnconfigure(1, weight=1)
        master_fr.columnconfigure(tk.ALL, pad=5)
        master_fr.rowconfigure(tk.ALL, pad=5)
    
    #---------------------------------------------------------------
    # Button actions
    #---------------------------------------------------------------
    def on_pb_color(self):
        color = colorchooser.askcolor(initialcolor=self.color)[0]
        if(color):
            self.color = (int(color[0]), int(color[1]), int(color[2]))
            self.pb_color.configure(bg="#%02X%02X%02X" % self.color)
        
    #---------------------------------------------------------------
    # Standard Action hooks
    #---------------------------------------------------------------
    def dlg_initialize(self):
        
        # Name
        self.txt_name.delete(0,tk.END)
        self.txt_name.insert(tk.END, self.T.name)
        
        # Delay
        self.sb_delay.delete(0,tk.END)
        self.sb_delay.insert(tk.END, self.T.delay)
        
        # Duration
        self.sb_duration.delete(0,tk.END)
        self.sb_duration.insert(tk.END, self.T.duration)
        
        # Color Chooser
        if(type(self.T.color) != colors.Color_rgb):
            raise TypeError("TODO: Support different color encodings")
        
        r = int(self.T.color.r * 255.0)
        g = int(self.T.color.g * 255.0)
        b = int(self.T.color.b * 255.0)
        self.color = (r,g,b)
        self.pb_color.configure(bg="#%02X%02X%02X" % self.color)
        
    def dlg_validate(self):
        
        #---------------
        # Validate name
        #---------------
        name = self.txt_name.get().strip()
        
        # check if name is acceptable
        if(len(name) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "Name cannot be empty."
            )
            return(False)
            
        # check if any other transitions have the same name
        for other_T in self.T_list:
            if(self.T is other_T):
                continue # skip self
            if(name == other_T.name):
                messagebox.showerror(
                    title = "Error!",
                    message = "Another transition already has the same name."
                )
                return(False)
        
        return(True)
    
    def dlg_apply(self):
        self.T.name = self.txt_name.get()
        self.T.delay = float(self.sb_delay.get())
        self.T.duration = float(self.sb_duration.get())
        self.T.color = colors.Color_rgb(*self.color)
    
#---------------------------------------------------------------------------------------------------
def EditTransition(parent, T, T_list = []):
    """
    Transition editor factory function
    T: Transition to edit
    T_list: List of other existing transitions
    """
    if(type(T) == eecfg.trans_Immediate):
        return(Edit_trans_Immediate(parent, T, T_list))
    elif(type(T) == eecfg.trans_Fade):
        return(Edit_trans_Fade(parent, T, T_list))
    elif(type(T) == eecfg.trans_Waveform):
        raise TypeError("TODO: Write me")
    else:
        raise TypeError("Bad type")
    
#===================================================================================================

class _ask_transition_type(object):
    def __init__(self, parent):
        self.tkWindow = tk.Toplevel(parent)
        self.tkWindow.transient(parent)
        self.tkWindow.parent = parent
        self.tkWindow.title("Type")
        self.result = None
        
        fr_body = ttk.Frame(
            self.tkWindow,
            padding = 5
        )
        fr_body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Buttons
        for t in eecfg.Transition.__subclasses__():
            tk.Button(
                fr_body,
                text= t.__name__,
                command=lambda t2=t:self.pb_select(t2)
            ).pack(fill=tk.X)
        
        # Place dialog on top of parent window
        self.tkWindow.grab_set()
        self.tkWindow.geometry("+%d+%d" % (self.tkWindow.parent.winfo_rootx()+50,
                                           self.tkWindow.parent.winfo_rooty()+50))
        
        # block until the window exits
        self.tkWindow.wait_window(self.tkWindow)
        
    def pb_select(self,t):
        self.result = t
        self.tkWindow.withdraw()
        self.tkWindow.update_idletasks()
        self.tkWindow.parent.focus_set()
        self.tkWindow.destroy()

class EditTransitionList(tkext.ListEdit):
    def __init__(self, parent, T_list = []):
        
        tkext.ListEdit.__init__(self, parent = parent, title = "Edit Transitions", item_list = T_list)
        
    def get_item_label(self, I):
        return("%s::%s" % (type(I).__name__, I.name))
    
    def new_item(self):
        
        # Display selector for which transition type
        dlg = _ask_transition_type(self.tkWindow)
        if(dlg.result == None):
            return(None)
        T_type = dlg.result
        
        # Create transition item
        T = T_type()
        T.name = "New Transition"
        
        # Open edit dialog
        dlg = EditTransition(self.tkWindow, T, self.item_list)
        if(dlg.result):
            return(dlg.T)
        else:
            return(None)
    
    def edit_item(self, I):
        dlg = EditTransition(self.tkWindow, I, self.item_list)
        if(dlg.result):
            return(dlg.T)
        else:
            return(None)
            
    def deleting_item(self, I):
        print("TODO: Check if other things are using the transition before deleting")
        return(True)
    
            