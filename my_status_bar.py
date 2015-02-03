#!/usr/bin/env python3
# -*- encode:utf-8 -*-

from tkinter import *

class my_status_bar(object):
    
    def __init__(self, master):
        self.frame = Frame(master, bd=2, relief=FLAT)
        self.frame.pack()
        
        self.yscrollbar = Scrollbar(self.frame)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        
        self.status_bar = Text(self.frame)
        self.status_bar.config(state=DISABLED) # ставим блокироку
        self.status_bar.config(bd=0, relief=GROOVE, bg="#D4D0C8") # украшательства
        self.status_bar.config(height=2, padx = 5, pady = 5, wrap=WORD) # высота в 2 строки
        self.yscrollbar.config(command=self.status_bar.yview)
        self.status_bar.config(yscrollcommand=self.yscrollbar.set)
        
    def push_text(self, text_content=''):
        """
        Ввод текста в статусную строку
        """
        self.status_bar.config(state=NORMAL) # снимаем блокировку
        self.status_bar.delete(1.0, END) # очищаем содержимое
        self.status_bar.insert(END, text_content)
        self.status_bar.config(state=DISABLED) # возвращаем блокировку
    
    def pack(self):
        self.status_bar.pack()

if __name__ == '__main__':
    root = Tk()

    tw = my_status_bar(root)

    tw.pack()

    tw.push_text("""Hello, World!       cccccccccccccccccccccccccc          dddddddddddddddddddddddddddddddddddddddd ssssssssssssssssssssssssssssssssssssssssssssssssssssssss aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    fffffffffffffffff""")


    root.mainloop()