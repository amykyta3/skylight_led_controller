
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ..python_modules import tk_extensions as tkext
from . import btLink
from . import settings

#---------------------------------------------------------------------------------------------------
def check_bt_addr():
    """
    Checks if bt_addr was set.
    If not, asks if user wants to go through the discovery process.
    Returns True if a valid bt_addr is/has been setup
    """
    if(settings.S_DATA.bt_addr != None):
        return(True)
    
    ans = messagebox.askyesno(
        title = "Bluetooth Device Unset",
        message = "A Bluetooth device has not been set.\nWould you like to discover devices now?"
    )
    
    if(ans):
        # do device inquiry
        
        def inquiry_job(dlg_if):
            dlg_if.set_status1("Searching for devices...")
            dlg_if.set_progress(50)
            devs = btLink.discover()
            return(devs)
        
        job = tkext.ProgressBox(
            job_func = inquiry_job,
            parent = None,
            title = "Searching for devices..."
        )
        
        if(job.job_retval == None):
            return(False)
        devs = job.job_retval
        
        # process results
        if(len(devs) == 0):
            messagebox.showerror(
                title = "Error!",
                message = "No devices found."
            )
            return(False)
        else:
            settings.S_DATA.bt_addr = devs[0][0]
            return(True)
    else:
        return(False)
    