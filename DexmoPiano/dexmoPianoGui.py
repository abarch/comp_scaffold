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


# directory/filename strings
outputSubdir = './output/'
inputMidiStrs = [outputSubdir + 'output.mid', outputSubdir + 'output-m.mid']
outputLyStr = outputSubdir + 'output-midi.ly'
outputPngStr = outputSubdir + 'output-midi.png'

GuidanceModeList = ["None", "At every note", "At every note (note C-G)", "Individual"]
guidanceMode = "At every note"
maxNotePerBar = 1
numberOfBars = 5
bpm = 120
noteValuesList = [1, 1/2, 1/4, 1/8]
pitchesList = [60, 62]
twoHandsBool = False
#outFiles = [inputMidiStr, outputSubdir + 'output-m.mid']

errors = []
changetask = []


# starts only metronome output and haptic impulse from dexmo for every note
def startTask():
    global errors

    # use MIDI file with metronome staff
    threadHandler.startThreads(inputMidiStrs[1], guidanceMode)

    errorvalue = threadHandler.get_errors()
    errors.append(abs(errorvalue))
    add_error_plot()


# starts Demo with sound output and haptic impulse from dexmo for every note
def startDemo():
    # use MIDI file with metronome staff
    dexmoOutput.play_demo(inputMidiStrs[1], guidanceMode)


# generate new midiFile and Notesheet and displays it
# dont generate new task if user opened a midi file
def nextTask(userSelectedTask=False, userSelectedLocation=inputMidiStrs[0]):
    if userSelectedTask == False:
        midiGen.generateMidi(bpm=bpm,
                             noteValues=noteValuesList,
                             notesPerBar=list(range(1, maxNotePerBar + 1)),
                             noOfBars=numberOfBars,
                             pitches=pitchesList,
                             #pitches=list(range(52, 68)),
                             twoHands=twoHandsBool,
                             outFiles=inputMidiStrs)

        subprocess.run(['midi2ly', inputMidiStrs[0], '--output=' + outputLyStr],
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
    if (dexmo_port.get() == "None"):
        global GuidanceModeList, guidanceMode
        GuidanceModeList = ["None"]
        guidanceMode = "None"
        if(mainWindow):
            add_Dexmo_Warning()


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
    global bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList, twoHandsBool, errors, changetask
    values = bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList, twoHandsBool
    options.changeParameter()

    newValues = options.get_data()
    # if parameters changed, delete errors to start a new diagram
    if values != newValues:
        errors = []
        changetask = []
    bpm, numberOfBars, maxNotePerBar, guidanceMode, noteValuesList, pitchesList, twoHandsBool = newValues


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


    chose_ports()


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

# chose sound, dexmo and inport ports in startmenu
def chose_ports():
    global dexmo_port
    # chose outport for dexmo/ legodexmo etc
    outports, inports = dexmoOutput.get_midi_interfaces()
    outports.append("None")
    inports.append("None")

    ## Dexmo Port
    l = Label(root, text=" Chose dexmo outport:")
    l.place(x=675, y=600, height=50, width=150)

    dexmo_port = StringVar(root)
    matching = [s for s in outports if "DEXMO" in s]
    if matching:
        midi_interface = matching[0]
        dexmo_port.set(midi_interface)
    else:
        dexmo_port.set("None")
    dexmoOptions = OptionMenu(root, dexmo_port, *outports, command = lambda event: dexmoOutput.set_dexmo(dexmo_port.get()))
    dexmoOutput.set_dexmo(dexmo_port.get())
    dexmoOptions.place(x=650, y=640, height=25, width=200)

    # Sound Port
    l1 = Label(root, text=" Chose sound outport:")
    l1.place(x=675, y=680, height=50, width=150)

    sound_port = StringVar(root)
    matching2 = [s for s in outports if "Qsynth" in s]
    if matching2:
        sound_interface = matching2[0]
        sound_port.set(sound_interface)
    else:
        sound_port.set("None")
    dexmoOutput.set_sound_outport(sound_port.get())
    soundOptions = OptionMenu(root, sound_port, *outports, command = lambda event: dexmoOutput.set_sound_outport(sound_port.get()))
    soundOptions.place(x=650, y=720, height=25, width=200)

    # Inport
    l2 = Label(root, text=" Chose inport:")
    l2.place(x=675, y=760, height=50, width=150)

    inport = StringVar(root)
    matching3 = [s for s in inports if "VMPK" in s]
    if matching3:
        inport_interface = matching3[0]
        inport.set(inport_interface)
    else:
        inport.set("None")
    threadHandler.set_inport(inport.get())
    inportOptions = OptionMenu(root, inport, *inports, command = lambda event: threadHandler.set_inport(inport.get()))
    inportOptions.place(x=650, y=800, height=25, width=200)



##_____________________________START LOOP HERE________________________________##


# create file output folder if it does not already exist
subprocess.run(['mkdir', '-p', outputSubdir], stderr=subprocess.DEVNULL)

# Create a window and title
root = Tk()
root.title("Piano with Dexmo")
load_Startmenu()
# Set the resolution of window
root.geometry("1500x1000")

# initialize keyboard input thread (done here to avoid multiple instances)
threadHandler.initInputThread()

check_dexmo_connected(mainWindow=False)
options = optionsWindowClass(root=root, guidanceModeList=GuidanceModeList, bpm=bpm, numberOfBars=numberOfBars, maxNoteperBar=maxNotePerBar,
                             noteValuesList=noteValuesList, pitchesList=pitchesList, guidanceMode=guidanceMode, twoHandsBool=twoHandsBool)

root.mainloop()
