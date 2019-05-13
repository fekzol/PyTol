# -*- coding: utf-8 -*-

import os, ctypes
from sys import platform
from datetime import datetime

def get_username():
    if platform == "linux" or platform == "linux2":
        import pwd
        name = pwd.getpwuid(os.getuid())[4].split(",")[0]
        #print name
        return name
    elif platform == "win32":
        name = get_win_display_name()
        #print name
        return name
    elif platform == "darwin":
        return "OS X"
    
def get_date():
    date = ""
    now = datetime.now()
    date = "%02d.%02d.%d" %(now.day, now.month, now.year)
    return date

def get_win_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3 #5 for email
 
    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)
 
    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)
    return nameBuffer.value

#print get_username()
#print get_date()
