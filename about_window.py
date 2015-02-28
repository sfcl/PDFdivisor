#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
import webbrowser

class about_box():

    def __init__(self, master, title, message, url):

        self.url_ = url
        self.message = message
        self.about_width = 300
        self.about_height = 150

        x = master.winfo_rootx()
        y = master.winfo_rooty()

        width = master.winfo_width()/2
        height = master.winfo_height()/2

        x = x + width - int(self.about_width/2)
        y = y + height - int(self.about_height/2)

        geom = "%dx%d+%d+%d" % (self.about_width, self.about_height, x, y)

        top = Toplevel(master)
        top.geometry(geom)
        top.title(title)

        msg = Label(top, text=self.message)
        msg.grid(column=0, row=0)

        url = Label(top, text=self.url_)
        url.config(fg="Blue", cursor="hand2")
        url.bind("<Button-1>", self.goto_home)
        url.grid(column=0, row=1)

        button = Button(top, text="OK", command=top.destroy)
        button.grid(column=0, row=4, padx=5, pady=5, sticky=W+E+N+S,)

    def goto_home(self, event):
        webbrowser.open_new(self.url_)