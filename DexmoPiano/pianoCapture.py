from tkinter import *
from  PIL import Image, ImageTk
import subprocess
import os
from midiInput import MidiInputThread
import mido
import makesongsly
import fileIO
import time

import threadHandler

# directory/filename strings
outputDir = './output/'
tempDir = './output/temp/'
inputFileStrs = [tempDir + 'output.mid', tempDir + 'output-m.mid', tempDir + 'output-md.mid', tempDir + 'output.xml']

midiInputPort = ''
midiOutputPort = ''
midiPopupMenu = 0

songNum = 0

midiSaved = False # Indicates if the output file was already created


# delete saved midis and XMLs from last programm run
def deleteOldFiles():
    files = os.listdir(outputDir)
    for item in files:
        if item.endswith('.mid') or item.endswith('.xml'):
            os.remove(os.path.join(outputDir, item))

def getCurrentTimestamp():
    """
    Receives and formats the current time and date.
    @return: Current timestamp (YearMonthDay-HourMinuteSecond).
    """
    return time.strftime("%Y%m%d-%H%M%S")


# generate new midiFile and note sheet and display it
# dont generate new task if user opened a midi file
def nextTask(userSelectedTask=False, userSelectedLocation=inputFileStrs[0]):
    global midiFileLocation, midiSaved
    
    guidance = 0
    timestr = getCurrentTimestamp()
    currentMidi = "midi_test"
    guidanceMode = "None"

    targetNotes, actualNotes, errorVal = threadHandler.startThreads(midiFileLocation,guidance)

    if not midiSaved:
        #saveMidiAndXML(targetNotes)
        midiSaved = True
        options = [1, True, "bla"]
        fileIO.createXML(outputDir, currentMidi, options, targetNotes)
        midiSaved = True

    # create entry containing actual notes in XML
    fileIO.createTrialEntry(outputDir, currentMidi, timestr, guidanceMode, actualNotes, errorVal)
    ###TODO: remove (testing)
    #fileIO.printXML(outputDir + currentMidi + ".xml", True)
    print("Created XML")

def load_songs():
    for k in range(10):
        Button(root,  text='Song ' + str(k+1), command=lambda k=k: playSong(k+1)).place(x=30, y=k*60+30, height=50, width=200)

# load start menu with button for first task and exit button
def load_Startmenu():
    global bpmSelected, playButton, connectButton
    
    playButton = Button(root, text='Play Music', command=nextTask)
    playButton.place(x=675, y=440, height=50, width=150)
    playButton["state"]= "disabled"
    Button(root, text='Quit', command=quit).place(x=1200, y=20, height=50, width=150)
    
    connectButton = Button(root, text='Connect', command=connectToMidi)
    connectButton.place(x=230, y = 640, height=50, width=200)
    connectButton["state"] = "disabled"
    
    Button(root, text='Refresh MIDI', command=refreshMidi).place(x=30, y = 640, height=50, width=200)

    bpms = [0] * (131-50)
    
    for bpm in range(50,131):
        bpms[bpm-50] = str(bpm)
        
    bpmSelected = StringVar(root)
    bpmSelected.set('60')
    
    bpmPopup = OptionMenu(root, bpmSelected, *bpms).place(x=1000, y=120, height=50, width=150)

    refreshMidi()
    
    midiInputPort, inputs_midi = getMidiInputs()
    midiOutputPort, outputs_midi = getMidiOutputs()
    
    if len(inputs_midi)>0 and len(outputs_midi)>0:
        print("setting state to normal")
        connectButton["state"] = "normal"

def connectToMidi():
    global playButton
    print("Connect to midi input: " + midiInputPort.get())
    result_input = threadHandler.set_inport(midiInputPort.get())
    
    print("Connect to midi output: " + midiOutputPort.get())
    result_output = threadHandler.set_outport(midiOutputPort.get())
    
    if result_input and result_output:
        playButton["state"] = "normal"

def refreshMidi():
    global midiInputPort, midiInputPopupMenu, midiOutputPort, midiOutputPopupMenu
    midiInputPort, inputs_midi = getMidiInputs()
    MidiInputPopupMenu = OptionMenu(root, midiInputPort, *inputs_midi).place(x=30, y=680, height=50, width=200)
    
    midiOutputPort, outputs_midi = getMidiOutputs()
    MidiOutputPopupMenu = OptionMenu(root, midiOutputPort, *outputs_midi).place(x=230, y=680, height=50, width=200)

def getMidiInputs():
    outputs_midi, inputs_midi  = get_midi_interfaces()
    midiInputPort = StringVar(root)
    if len(inputs_midi)==0:
        midiInputPort.set('')
        inputs_midi = {''}
    else:
        midiInputPort.set(inputs_midi[0])
    return midiInputPort, inputs_midi
    
def getMidiOutputs():
    outputs_midi, inputs_midi  = get_midi_interfaces()
    midiOutputPort = StringVar(root)
    if len(outputs_midi)==0:
        midiOutputPort.set('')
        outputs_midi = {''}
    else:
        midiOutputPort.set(outputs_midi[0])
    return midiOutputPort, outputs_midi
    
def playSong(songNumSelected):
    global midiFileLocation, songNum
    bpm = int(bpmSelected.get())
    print("Song "  + str(songNumSelected) + " pressed, bpm = " + str(bpm))
    # Create a midi file at the appropriate bpm
    makesongsly.make_song(songNumSelected, bpm)
    # use lilypad to make the sheet music  + midi
    load_notesheet('songs/song' + str(songNumSelected) + '.png')
    midiFileLocation = 'songs/song' + str(songNumSelected) + '.midi'
    songNum = songNumSelected

# loads notesheet for actual task
def load_notesheet(png):
    global background
    background = Image.open(png)
    background = background.convert("RGBA")
    width, height = background.size

    img = ImageTk.PhotoImage(background)
    panel = Label(root, image=img)
    panel.image = img
    panel.place(x=300, y=20, width=width, height=height)
    
def get_midi_interfaces():
    return mido.get_output_names(), mido.get_input_names()

# program starts here

# create file output folder if it does not already exist
subprocess.run(['mkdir', '-p', tempDir], stderr=subprocess.DEVNULL)
# Create a window and title
root = Tk()
root.title("Piano capture")

deleteOldFiles()

# initialize keyboard input and output threads
threadHandler.initInputThread()
threadHandler.initOutputThread()

load_Startmenu()
load_songs()
# Set the resolution of window
root.geometry("1500x1000")

root.mainloop()
