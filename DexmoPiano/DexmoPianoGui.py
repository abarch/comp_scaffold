from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import numpy as py
import time
import os
import DexmoOutput
import midiGen


# starts only metronome output and haptic impulse from dexmo for every note
# TODO generate personal user feedback in DexmoOutput, depending on errors
def startTask():
    DexmoOutput.practice_task('output.mid')


# starts Demo with sound output and haptic impulse from dexmo for every note
def startDemo():
    DexmoOutput.play_demo('output.mid')


# generate new midiFile and Notesheet and displays it
# TODO generate MidiFile with arguments out of errors
def nextTask():
    midiGen.generateMidi()
    os.system('midi2ly output.mid')
    os.system('lilypond -fpng output-midi.ly')
    clearFrame()
    load_Notesheet("output-midi.png")
    load_taskButtons()

# loads notesheet for actual task
def load_Notesheet(png):
    global background
    background = Image.open(png)
    background = background.convert("RGBA")
    global width, height
    width, height = background.size

    img = ImageTk.PhotoImage(background)
    # create a label
    panel = Label(root, image = img)
    # set the image as img
    panel.image = img
    panel.pack(side = RIGHT)

# create button for demo, practicing, next task, back to start menu
def load_taskButtons():
    startMenuButton = Button(root, text ='Back to Menu',
        command = backToMenu).place(x = 10, y = 940, height=50, width=150)
    startTaskcButton = Button(root, text ='Start Task',
        command = startTask).place(x = 10, y = 100, height=50, width=150)
    startDemoButton = Button(root, text ='Start Demo',
        command = startDemo).place(x = 10, y = 160, height=50, width=150)
    nextTaskButton = Button(root, text ='Next Task',
        command = nextTask).place(x = 10, y = 400, height=50, width=150)


# load start menu with button for first task and exit button
def load_Startmenu():
    nextTaskButton = Button(root, text ='Start first task',
        command = nextTask).place(x = 425, y = 440, height=50, width=150)
    startDemoButton = Button(root, text ='Quit',
        command = quit).place(x = 425, y = 500, height=50, width=150)

# destroy all widgets from frame
def clearFrame():
    for widget in root.winfo_children():
       widget.destroy()

# go back to start menu
def backToMenu():
    clearFrame()
    load_Startmenu()

# wuit "Piano with dexmo"
def quit():
    root.destroy()

##_____________________________START LOOP HERE________________________________##

# Create a window and title
root = Tk()
root.title("Piano with Dexmo")

load_Startmenu()
# Set the resolution of window
root.geometry("1000x1000")

root.mainloop()
