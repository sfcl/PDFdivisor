#!/usr/bin/env python3
# -*- encode:utf-8 -*-

from tkinter import *
from configuration import app_conf as ac

class my_status_bar(object):
    
    def __init__(self, master,):
        self.frame = Frame(master, bd=2, relief=FLAT)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.config(bg=ac.bg)

        self.yscrollbar = Scrollbar(self.frame)
        self.yscrollbar.grid(row=0, column=1, sticky=N+S)

        self.status_bar = Text(self.frame)
        self.status_bar.config(state=DISABLED) # ставим блокироку
        self.status_bar.config(bd=0, relief=GROOVE, bg=ac.bg) # украшательства
        self.status_bar.config(height=2, padx = 5, pady = 5, wrap=WORD) # высота в 2 строки
        self.yscrollbar.config(command=self.status_bar.yview)
        self.status_bar.config(yscrollcommand=self.yscrollbar.set)

        self.status_bar.grid(row=0, column=0)

    def push_text(self, text_content=''):
        """
        Ввод текста в статусную строку
        """
        self.status_bar.config(state=NORMAL) # снимаем блокировку
        self.status_bar.delete(1.0, END) # очищаем содержимое
        self.status_bar.insert(END, text_content)
        self.status_bar.config(state=DISABLED) # возвращаем блокировку
    
    #def pack(self):
    #    self.status_bar.pack()

    def grid(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky=N+S+E+W)
    #    self.status_bar.grid(row=row, column=column)
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def winfo_width(self):
        self.frame.update()
        return self.frame.winfo_height()

if __name__ == '__main__':
    root = Tk()

    tw = my_status_bar(root)

    tw.pack()

    tw.push_text("Hello, World!")
    root.mainloop()