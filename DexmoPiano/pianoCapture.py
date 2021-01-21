from tkinter import *
from  PIL import Image, ImageTk
import subprocess
import os
from midiInput import MidiInputThread
import mido
import makesongsly
import fileIO
import time
#import visualNotes
from threading import Thread

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
    global midiFileLocation, midiSaved, alien1

    #alien1 = canvas.create_oval(20 + 90, 260 - 130, 40 + 90, 300 - 130, outline='white', fill='blue')
    canvas.itemconfigure(alien1, fill='blue')
    canvas.coords(alien1,20+90 , 260-130 , 40+90 , 300 -130)
  #  curserThread = Thread(target = movement)
    curserThread = Thread(target=animation_test)

    guidance = 0
    timestr = getCurrentTimestamp()
    currentMidi = "midi_test"
    guidanceMode = "None"

 #   root.after(0, animation_test)
    curserThread.start()
    #targetNotes, actualNotes, errorVal = threadHandler.startThreads(midiFileLocation,guidance)
    recThread = Thread(target=threadHandler.startThreads, args=(midiFileLocation, guidance))
 #   recThread = Thread(target=threadHandler.startRecordThread, args=(midiFileLocation, guidance))
   # targetNotes, actualNotes, errorVal = threadHandler.startRecordThread(midiFileLocation, guidance)
    recThread.start()
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

def movement():
    global alien1
    # This is where the move() method is called
    # This moves the rectangle to x, y coordinates

    print("move.")
 #   canvas.move(alien1, 5, 0)
  #  canvas.pack()
    #canvas.draw() not working
    canvas.after(1, movement)

def animation_test():
    global alien1, bpmSelected

    bpm = int(bpmSelected.get())
    bars = 8
    song_length_pixels = 123*5
    correction = 50
    track = 0
    while track==0:
        dx = 1
        y = 0
        if track == 0:
            for i in range(0, 123*5):
               # print("i ",i)
              #  time.sleep(1)
                canvas.move(alien1, dx, y)
               # canvas.update()
               # canvas.update_idletasks()
                # canvas.draw() not working
                #time.sleep(32.0/(125*5))
               # print(60.0*4*bars*dx/(song_length_pixels*bpm))
                time.sleep(60.0*4*bars*dx/((song_length_pixels+correction)*bpm))
            track = 1
            print("check")

        else:
            for i in range(0, 51):
                time.sleep(1)
                canvas.move(alien1, -x, y)
                canvas.update()
            track = 0
        print(track)

# load start menu with button for first task and exit button
def load_Startmenu():
    global bpmSelected, playButton, connectButton
    global alien1
    playButton = Button(root, text='Play Music', command=nextTask)
    playButton.place(x=675, y=440, height=50, width=150)
    playButton["state"]= "disabled"

    # playButton = Button(root, text='Test', command=nextTask)
    # playButton.place(x=675, y=540, height=50, width=150)
    # playButton["state"] = "active"


    alien1 = canvas.create_oval(20+90, 260-130, 40+90, 300-130, outline='white', fill='white')
    canvas.pack()

#    canvas2 = Canvas(root, width=300, height=300)
#    canvas2.pack()
    piano_img = ImageTk.PhotoImage(Image.open("piano_notes.png"))
    canvas.create_image(0 , 0, anchor=NW, image=piano_img)
    canvas.pack()
#    movement()
 #   root.after(0, animation_test)

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
    
    bpmPopup = OptionMenu(root, bpmSelected, *bpms).place(x=1000, y=120+100, height=50, width=150)

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
canvas = Canvas(root, width=750, height = 800, bg='white')
#canvas2 = Canvas(root, width = 300, height = 300)
#canvas2.pack()
img = ImageTk.PhotoImage(Image.open("piano_notes.png"))
canvas.create_image(110, 500, anchor=NW, image=img)
#Notes.create_visual_notes(canvas)

deleteOldFiles()

# initialize keyboard input and output threads
threadHandler.initInputThread()
threadHandler.initOutputThread()

load_Startmenu()
load_songs()
# Set the resolution of window
root.geometry("1500x1000")

root.mainloop()
