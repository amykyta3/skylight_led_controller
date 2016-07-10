
import tkinter as tk
from tkinter import ttk
from ..python_modules import tk_extensions as tkext
from . import settings

#---------------------------------------------------------------------------------------------------
class Terminal(tkext.Dialog):
    def __init__(self, parent, btlink):
        self.btlink = btlink
        
        # Start the dialog. This blocks until done.
        tkext.Dialog.__init__(self, parent = parent, title = "Terminal")
        
    #---------------------------------------------------------------
    def create_body(self, master_fr):
        # Construct the contents of the dialog
        
        self.txt_console = tk.Text(
            master_fr,
            wrap = tk.WORD,
            width = 80,
            height = 30,
            bg="black",
            fg="white"
        )
        self.txt_console.pack(
            fill = tk.X,
            expand = True
        )
        self.txt_console.configure(state=tk.DISABLED)
        
        

    #---------------------------------------------------------------
    def dlg_initialize(self):
        self.tkWindow.bind("<Key>", self.keypress)
        
        self.btlink.cmd("echo 1\r\n")
        self.btlink.S.setblocking(False)
        
        self.timer = tkext.Timer(self.tkWindow, 100, self.get_input)
        self.timer.start()
        
    def keypress(self, event):
        if(len(event.char) == 0):
            return
        
        c = event.char.encode("ascii")
        self.btlink.S.send(c)
        
    def get_input(self):
        try:
            rxd = self.btlink.S.recv(1024).decode("ascii")
        except:
            return
        
        self.txt_console.configure(state=tk.NORMAL)
        for c in rxd:
            if(c == '\r'):
                pass
            elif(c == '\b'):
                # backspace
                self.txt_console.delete("end-2c", tk.END)
            else:
                self.txt_console.insert(tk.END, c)
        self.txt_console.yview_moveto(1.0)
        self.txt_console.configure(state=tk.DISABLED)