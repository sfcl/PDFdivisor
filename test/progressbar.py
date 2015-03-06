#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import threading
import queue
from tkinter import ttk
import time

class GuiPart:
    def __init__(self, master, queue):
        self.queue = queue
        self.pgBar = ttk.Progressbar(master, orient='horizontal',
                                     length=300, mode='determinate')
        self.lb = tk.Listbox(master, width=20, height=5)
        self.pgBar.grid(padx=20, pady=20)
        self.lb.grid(row=1, column=0, padx=20, pady=20)
    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.lb.insert('end', msg)
                self.pgBar.step(25)
            except queue.Empty:
                pass

class ThreadedClient:
    def __init__(self, master):
        self.master = master
        self.queue = queue.Queue()
        self.gui = GuiPart(master, self.queue)
        self.running = True
        threading.Thread(target=self.workerThread).start()
        self.periodicCall()
    def periodicCall(self):
        self.gui.processIncoming()
        if self.running:
            self.master.after(100, self.periodicCall)
    def workerThread(self):
        for x in range(1, 5):
            time.sleep(2)
            msg = "Function %s finished..." % x
            self.queue.put(msg)
        self.running = False

root = tk.Tk()
client = ThreadedClient(root)
root.mainloop()
