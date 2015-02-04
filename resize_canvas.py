#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *

class ScrolledCanvas(Canvas):
    '''
    Контейнер с канвой. В него автоматически добвляется правый скролбар
    '''
    def __init__(self, container, **kwargs):
        Canvas.__init__(self, container)
        self.update_idletasks()
        self.config(borderwidth=0)
        self.config(**kwargs)
        vbar = Scrollbar(container)

        vbar.pack(side=RIGHT,  fill=Y)                 # pack canvas after bars
        self.pack(side=TOP, fill=BOTH, expand=YES)

        vbar.config(command=self.yview)                # call on scroll move
        self.config(yscrollcommand=vbar.set)           # call on canvas move