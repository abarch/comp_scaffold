from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess

import dexmoOutput
import midiGen
from optionsWindow import optionsWindowClass
import threadHandler


GuidanceModeList = ["None", "At every note", "Individual"]
guidanceMode = "At every note"
maxNotePerBar = 1
numberOfBars = 5
bpm = 120
noteValuesList = [1, 1/2, 1/4, 1/8]
pitchesList = [62, 64]
outFile="./output/output.mid"

errors = []
changetask = []

# directory/filename strings
outputSubdir = './output/'
inputMidiStr = outputSubdir + 'output.mid'
outputLyStr = outputSubdir + 'output-midi.ly'
outputPngStr = outputSubdir + 'output-midi.png'


# starts only metronome output and haptic impulse from dexmo for every note
def startTask():
    global errors

    threadHandler.startThreads(inputMidiStr, guidanceMode)

    errorvalue = threadHandler.get_errors()
    errors.append(abs(errorvalue))
    add_error_plot()


# starts Demo with sound output and haptic impulse from dexmo for every note
def startDemo():
    dexmoOutput.play_demo(inputMidiStr, guidanceMode)


# generate new midiFile and Notesheet and displays it
# dont generate new task if user opened a midi file
def nextTask(userSelectedTask=False, userSelectedLocation=inputMidiStr):
    if userSelectedTask == False:
        midiGen.generateMidi(bpm=bpm, noteValues=noteValuesList,
                             notesPerBar=list(range(1, maxNotePerBar + 1)),
                             noOfBars=numberOfBars, pitches=pitchesList, outFile=outFile)

        subprocess.run(['midi2ly', inputMidiStr, '--output=' + outputLyStr],
                       stderr=subprocess.DEVNULL)

    else:
        subprocess.run(['midi2ly', userSelectedLocation, '--output=' + outputLyStr],
                       stderr=subprocess.DEVNULL)

    subprocess.run(['lilypond', '--png', '-o', outputSubdir, outputLyStr],
                   stderr=subprocess.DEVNULL)
    clearFrame()
    load_notesheet(outputPngStr)

    check_dexmo_connected(mainWindow=True)
    load_taskButtons()

    # if task is changed remember trial to show in visualisation
    if errors:
        changetask.append(len(errors))

    add_error_plot()


# check if dexmo is connected and change possible guidance modes
def check_dexmo_connected(mainWindow):
    if (dexmoOutput.check_Dexmo() == False):
        global GuidanceModeList, guidanceMode
        GuidanceModeList = ["None"]
        guidanceMode = "None"
        if(mainWindow):
            add_Dexmo_Warning()
    else:
        GuidanceModeList = ["None", "At every note", "Individual"]


# loads notesheet for actual task
def load_notesheet(png):
    global background
    background = Image.open(png)
    background = background.convert("RGBA")
    global width, height
    width, height = background.size

    img = ImageTk.PhotoImage(background)
    panel = Label(root, image=img)
    panel.image = img
    panel.place(x=170, y=0, width=835, height=1181)


##_______________________________OPTIONS______________________________________##

def specifyTask():
    global bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList, errors, changetask
    values = bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList
    options.changeParameter()

    newValues = options.get_data()
    # if parameters changed, delete errors to start a new diagram
    if values != newValues:
        errors = []
        changetask = []
    bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList = newValues


##_____________________________ERROR-PLOT_____________________________________##

def add_error_plot():
    Label(root, text=" Error visualization:").place(x=1200, y=10, width=150, height=20)

    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    np.linspace(0, 10, 1000)

    xvalues = []
    for i in range(len(errors)):
        xvalues.append(i + 1)
    axis.plot(xvalues, errors, label="General error", marker='o')

    if (changetask):
        for i in changetask:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # axis.set_xticks(xvalues)
    axis.set_yticks([0, 1, 2, 3])
    axis.set_ylim(0, 4)
    axis.set_xlabel("Trials")
    axis.set_ylabel("Error")

    # axis.legend()
    axis.grid()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.place(x=1050, y=30, width=400, height=400)

    global checkbox, details
    details = BooleanVar()
    details.set(False)
    checkbox = Checkbutton(root, text='show error details', command=add_error_details, var=details)
    checkbox.place(x=1050, y=440)


def add_error_details():
    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    x = np.linspace(0, 10, 1000)

    xvalues = []
    for i in range(len(errors)):
        xvalues.append(i + 1)
    axis.plot(xvalues, errors, label="General error", marker='o')

    if (changetask):
        for i in changetask:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # axis.set_xticks(xvalues)
    axis.set_yticks([0, 1, 2, 3])
    axis.set_ylim(0, 4)
    axis.set_xlabel("Trials")
    axis.set_ylabel("Error")

    # axis.plot(x, np.sin(x), "-r", label = "Tempo", marker='o')
    # axis.plot(x, np.cos(x), "-g", label = "Notes", marker='o')
    # axis.plot(x, np.tan(x), "--y", label = "etc", marker='o')
    axis.plot(x, np.sin(x), "-r", label="Tempo")
    axis.plot(x, np.cos(x), "-g", label="Notes")
    axis.plot(x, np.tan(x), "--y", label="etc")

    axis.legend(loc='upper right')
    axis.grid()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.place(x=1050, y=30, width=400, height=400)

    global checkbox, details
    details = BooleanVar()
    details.set(True)
    checkbox = Checkbutton(root, text='show error details', command=add_error_plot, var=details)
    checkbox.place(x=1050, y=440)


##____________________________________________________________________________##


# create warning if Dexmo is not plugged in
def add_Dexmo_Warning():
    Label(root, text=" Warning: \n No Dexmo connected, \n no guidance possible.",
              fg="red").place(x=10, y=230, width=150, height=70)


# create button for demo, practicing, next task, back to start menu
def load_taskButtons():
    Button(root, text='Start Task', command=startTask).place(x=10, y=100, height=50, width=150)
    Button(root, text='Start Demo', command=startDemo).place(x=10, y=160, height=50, width=150)

    Button(root, text='Next Task', command=nextTask).place(x=10, y=400, height=50, width=150)
    Button(root, text='Specify next Task', command=specifyTask).place(x=10, y=460, height=25, width=150)

    Button(root, text='Open Midi file', command=openfile).place(x=10, y=520, height=25, width=150)

    Button(root, text='Back to Menu', command=backToMenu).place(x=10, y=940, height=50, width=150)

# open midi file user can choose
def openfile():
    nextTask(userSelectedTask=True, userSelectedLocation=filedialog.askopenfilename(filetypes=[("Midi files", ".midi .mid")]))


# load start menu with button for first task and exit button
def load_Startmenu():
    Button(root, text='Start first task', command=nextTask).place(x=675, y=440, height=50, width=150)
    Button(root, text='Quit', command=quit).place(x=675, y=500, height=50, width=150)


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


# create file output folder if it does not already exist
subprocess.run(['mkdir', '-p', outputSubdir], stderr=subprocess.DEVNULL)

# initialize keyboard input thread (done here to avoid multiple instances)
threadHandler.initInputThread()

# Create a window and title
root = Tk()
root.title("Piano with Dexmo")
load_Startmenu()
# Set the resolution of window
root.geometry("1500x1000")

check_dexmo_connected(mainWindow=False)
options = optionsWindowClass(root=root, guidanceModeList=GuidanceModeList, bpm=bpm, numberOfBars=numberOfBars, maxNoteperBar=maxNotePerBar,
                             noteValuesList=noteValuesList, pitchesList=pitchesList, guidanceMode=guidanceMode)

root.mainloop()
