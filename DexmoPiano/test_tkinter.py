#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 15:10:45 2021

@author: bobby2
"""

import tkinter as tk
import threading
import time
 
# class ChangeText:
#     def __init__(self, parent):
#         self.parent = parent
#         self.label = tk.Label(self.parent)
#         self.label['text'] = 'Start Text'
#         self.label.pack()
#         self.update()
 
#     def update(self):
#         self.label['text'] = 'Updating in 10'
#         self.i = 10
#         self.timer()
 
#     def run_timer(self):
#         if self.i >= 0:
#             self.i -= 1
 
#     def timer(self):
#         self.run_timer()
#         if self.i >= 0:
#             self.label.after(1000, self.timer)
#             self.label['text'] = f'Updating in {self.i}'
#         else:
#             self.label['text'] = f'Done!'
 
 
 
 
# def main():
root = tk.Tk()
root.geometry('400x300+100+100')
root.title('Change Text')

def lol():
    for i in range(5):
        root["bg"] = "blue"
        time.sleep(3)
        root["bg"] = "red"
        time.sleep(3)

def kill_main():
    time.sleep(7)
    root.destroy()

threading.Thread(target=lol).start()
ui = threading.Thread(target=kill_main).start()
root.mainloop()

# ui.terminate()



# if __name__ == '__main__':
#     main()