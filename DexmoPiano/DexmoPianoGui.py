from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import numpy as py
import time
import os
import DexmoOutput
import midiGen
import threadHandler

global bpm, numberOfBars, noteValuesList, pitchesList, maxNoteperBar
guidanceMode = "At every note"
maxNoteperBar = 1
numberOfBars = 8
bpm = 120
noteValuesList = [1, 1/2, 1/4, 1/8]
pitchesList = [60, 62, 64, 65, 67, 69, 71, 72]


# starts only metronome output and haptic impulse from dexmo for every note
def startTask():
    threadHandler.startThreads('output.mid', guidanceMode)
    #DexmoOutput.practice_task('output.mid')

# starts Demo with sound output and haptic impulse from dexmo for every note
def startDemo():
    DexmoOutput.play_demo('output.mid')

# generate new midiFile and Notesheet and displays it
def nextTask():
    midiGen.generateMidi(bpm=bpm, noteValues=noteValuesList,
    				 notesPerBar=list(range(1, maxNoteperBar+1)),
    				 noOfBars=numberOfBars, pitches=pitchesList)
    os.system('midi2ly output.mid')
    os.system('lilypond --png output-midi.ly')
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
    panel = Label(root, image = img)
    panel.image = img
    panel.pack(side = RIGHT)

##_______________________________OPTIONS______________________________________##
# create Window to specify next task, root waiting until this window is closed
def spezifyTask():
    global specifyWindow
    specifyWindow = Toplevel(root)

    specifyWindow.transient(root)
    specifyWindow.grab_set()
    specifyWindow.geometry("310x540")
    specifyWindow.title("Options for next task")

## NOTEVALUE checkboxes
    l1 = Label(specifyWindow, text=" Notevalues:")
    l1.grid (row=1,columnspan=4,sticky=W, pady=(20,0))

    global fullNote, halfNote, quarterNote, eighthNote, sixteenthNote

    fullNote = BooleanVar()
    fullNote.set(1 in noteValuesList)
    chk1 = Checkbutton(specifyWindow, text='1', var=fullNote)
    chk1.grid(column=1, row=2)

    halfNote = BooleanVar()
    halfNote.set(1/2 in noteValuesList)
    chk1_2 = Checkbutton(specifyWindow, text='1/2', var=halfNote)
    chk1_2.grid(column=2, row=2)

    quarterNote = BooleanVar()
    quarterNote.set(1/4 in noteValuesList)
    chk1_4 = Checkbutton(specifyWindow, text='1/4', var=quarterNote)
    chk1_4.grid(column=3, row=2)

    eighthNote = BooleanVar()
    eighthNote.set(1/8 in noteValuesList)
    chk1_8 = Checkbutton(specifyWindow, text='1/8', var=eighthNote)
    chk1_8.grid(column=4, row=2)

    sixteenthNote = BooleanVar()
    sixteenthNote.set(1/16 in noteValuesList)
    chk1_16 = Checkbutton(specifyWindow, text='1/16', var=sixteenthNote)
    chk1_16.grid(column=5, row=2)

## Max notes per bar
    l2 = Label(specifyWindow, text=" Maximal note number per bar:")
    l2.grid(row=3,columnspan=4, sticky=W, pady=(20,0))

    OptionList = ["1","2","3","4"]
    maxNoteNumber = StringVar(specifyWindow)
    maxNoteNumber.set(maxNoteperBar)

    opt = OptionMenu(specifyWindow, maxNoteNumber, *OptionList)
    opt.grid(row=4,columnspan=4,sticky=W,)

## Number of Bars
    l3 = Label(specifyWindow, text=" Number of bars:")
    l3.grid(row=5,columnspan=4, sticky=W, pady=(20,0))

    numberBars = Scale(specifyWindow, from_=2, to=30, orient=HORIZONTAL)
    numberBars.grid(row=6, columnspan=4,sticky=W,)
    numberBars.set(numberOfBars)

## Beats per minute
    l4 = Label(specifyWindow, text=" Beats per minute:")
    l4.grid(row=7,columnspan=4, sticky=W, pady=(20,0))

    bpmscale = Scale(specifyWindow, from_=60, to=200, orient=HORIZONTAL)
    bpmscale.grid(row=8, columnspan=4,sticky=W,)
    bpmscale.set(bpm)

## NOTEPITCHES checkboxes
    l5 = Label(specifyWindow, text=" Notepitches:")
    l5.grid (row=9,columnspan=4,sticky=W, pady=(20,0))

    global C, D, E, F, G, A, B, C5

    C = BooleanVar()
    C.set(60 in pitchesList)
    c1 = Checkbutton(specifyWindow, text='C', var=C)
    c1.grid(column=1, row=10)

    D = BooleanVar()
    D.set(62 in pitchesList)
    d1 = Checkbutton(specifyWindow, text='D', var=D)
    d1.grid(column=2, row=10)

    E = BooleanVar()
    E.set(64 in pitchesList)
    e1 = Checkbutton(specifyWindow, text='E', var=E)
    e1.grid(column=3, row=10)

    F = BooleanVar()
    F.set(65 in pitchesList)
    f1 = Checkbutton(specifyWindow, text='F', var=F)
    f1.grid(column=4, row=10)

    G = BooleanVar()
    G.set(67 in pitchesList)
    g1 = Checkbutton(specifyWindow, text='G', var=G)
    g1.grid(column=5, row=10)

    A = BooleanVar()
    A.set(69 in pitchesList)
    a1 = Checkbutton(specifyWindow, text='A', var=A)
    a1.grid(column=1, row=11)

    B = BooleanVar()
    B.set(71 in pitchesList)
    b1 = Checkbutton(specifyWindow, text='B', var=B)
    b1.grid(column=2, row=11)

    C5 = BooleanVar()
    C5.set(72 in pitchesList)
    c5 = Checkbutton(specifyWindow, text='C5', var=C5)
    c5.grid(column=3, row=11)

## Max notes per bar
    l6 = Label(specifyWindow, text=" Guidance mode:")
    l6.grid(row=12,columnspan=4, sticky=W, pady=(20,0))


    GuidanceModeList = ["None","At every note","Individual"]
    guidance = StringVar(specifyWindow)
    guidance.set(guidanceMode)
    guideopt = OptionMenu(specifyWindow, guidance, *GuidanceModeList)
    guideopt.grid(row=13,columnspan=6,sticky=W,)


## Save and quit button

    l7 = Label(specifyWindow, text=" \n \n ")
    l7.grid(row=14,columnspan=4, sticky=W)

    saveButton = Button(specifyWindow, text ='Save and quit',
        command =lambda: save_settings(saveBPM=bpmscale.get(), saveBarNumber=numberBars.get(),
                        saveNotesperBar=maxNoteNumber.get(), saveGuidance=guidance.get()))
    saveButton.grid(row= 15, column = 4, columnspan = 3, pady=(20,0))

    quitButton = Button(specifyWindow, text ='Quit without saving',command =lambda: quit_options())
    quitButton.grid(row= 15, columnspan = 3, pady=(20,0))

    root.wait_window(specifyWindow)

def get_noteValues():
    noteValuesList = []
    if (fullNote.get() == True):
        noteValuesList.append(1)
    if (halfNote.get() == True):
        noteValuesList.append(1/2)
    if (quarterNote.get() == True):
        noteValuesList.append(1/4)
    if (eighthNote.get() == True):
        noteValuesList.append(1/8)
    if (sixteenthNote.get() == True):
        noteValuesList.append(1/16)

    return noteValuesList

def get_pitches():
    pitchesList = []
    if(C.get() == True):
        pitchesList.append(60)
    if(D.get() == True):
        pitchesList.append(62)
    if(E.get() == True):
        pitchesList.append(64)
    if(F.get() == True):
        pitchesList.append(65)
    if(G.get() == True):
        pitchesList.append(67)
    if(A.get() == True):
        pitchesList.append(69)
    if(B.get() == True):
        pitchesList.append(71)
    if(C5.get() == True):
        pitchesList.append(72)

    return pitchesList

def show_empty_list_error():
    l7 = Label(specifyWindow, text=" Error: \n At least one pitch and one \n notevalue must be selected.",
		 fg = "red")
    l7.grid(row=14,column = 2, columnspan=4, sticky=W)

# save settings to generate a new task with it
def save_settings(saveBPM, saveBarNumber, saveNotesperBar, saveGuidance):
    global bpm, numberOfBars, maxNoteperBar, guidanceMode, noteValuesList, pitchesList
    if not get_noteValues() or not get_pitches():
        show_empty_list_error()
    else:
        bpm = saveBPM
        numberOfBars = saveBarNumber
        maxNoteperBar = int(saveNotesperBar)
        guidanceMode = saveGuidance
        noteValuesList = get_noteValues()
        pitchesList = get_pitches()
        specifyWindow.destroy()

# quit options window without saving settings
def quit_options():
    specifyWindow.destroy()

##____________________________OPTIONS-END_____________________________________##


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
    nextTaskButton = Button(root, text ='Specify next Task',
        command = spezifyTask).place(x = 10, y = 460, height=25, width=150)

# load start menu with button for first task and exit button
def load_Startmenu():
    nextTaskButton = Button(root, text ='Start first task',
        command = nextTask).place(x = 425, y = 440, height=50, width=150)
    quitButton = Button(root, text ='Quit',
        command = quit).place(x = 425, y = 500, height=50, width=150)

# destroy all widgets from frame
def clearFrame():
    for widget in root.winfo_children():
       widget.destroy()

# go back to start menu
def backToMenu():
    clearFrame()
    load_Startmenu()

# quit "Piano with dexmo"
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
