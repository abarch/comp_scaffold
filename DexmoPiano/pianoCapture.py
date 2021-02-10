from tkinter import *
from  PIL import Image, ImageTk
import subprocess
import os
import mido
import makesongsly
import time
#import visualNotes
from threading import Thread
import datetime
import threadHandler
import queue
import config

midiInputPort = ''
midiOutputPort = ''
midiPopupMenu = 0
midiConnected = 0

songNum: int = 0 # which song to play
generatedBpm: int = 0 # bpm to play the song back at

midiSaved = False # Indicates if the output file was already created

# delete saved midis and XMLs from last programm run
def deleteOldFiles():
    files = os.listdir(config.outputDir)
    for item in files:
        if item.endswith('.mid') or item.endswith('.xml'):
            os.remove(os.path.join(config.outputDir, item))

def getCurrentTimestamp():
    """
    Receives and formats the current time and date.
    @return: Current timestamp (YearMonthDay-HourMinuteSecond).
    """
    return time.strftime("%Y%m%d-%H%M%S")

# generate new midiFile and note sheet and display it
# dont generate new task if user opened a midi file
def nextTask(finishAfterSong,userSelectedTask=False, userSelectedLocation=config.inputFileStrs[0]):
    global midiFileLocation, midiSaved, alien1, generatedBpm, bpmSelected

    bpm = int(bpmSelected.get())

    # If the bpm has changed since the midi file was generated, regenerate
    if bpm != generatedBpm:
        makesongsly.make_song(songNum, bpm)

    que = queue.Queue()
    config.str_date = datetime.datetime.today().strftime('_%Y_%m_%d_%H_%M_%S_')
    config.participant_id = id_textbox.get("1.0",'end-1c')
    config.freetext = freetext.get("1.0",'end-1c')
    #alien1 = canvas.create_oval(20 + 90, 260 - 130, 40 + 90, 300 - 130, outline='white', fill='blue')
    canvas.itemconfigure(alien1, fill='blue')
    canvas.coords(alien1,20+90 , 260-130 , 40+90 , 300 -130)

    guidance = 0
    config.timestr = getCurrentTimestamp()
    config.guidanceMode = "None"

# run the animation. for some reason it is delayed when using join() later.. TBD:FIX
    #curserThread = Thread(target=animation_test)
    #curserThread.start()

    # run in a thread with queue in order to get returned values
    recPlayThread = Thread(target=lambda q, arg1, arg2, arg3: q.put(threadHandler.startThreads(arg1, arg2, arg3)),
                           args=(que, midiFileLocation, guidance, finishAfterSong))

    # run the thread
    recPlayThread.start()

# don't play the song - wait until the stop button is pressed
def nextTaskAlone(userSelectedTask=False, userSelectedLocation=config.inputFileStrs[0]):
    global midiFileLocation, midiSaved, alien1, generatedBpm

    # Turn on the stop button
    config.stopButton["state"] = "active"

    # force a redraw
    root.update()

    bpm = int(bpmSelected.get())

    # If the bpm has changed since the midi file was generated, regenerate
    if bpm != generatedBpm:
        makesongsly.make_song(songNum, bpm)

    que = queue.Queue()
    config.str_date = datetime.datetime.today().strftime('_%Y_%m_%d_%H_%M_%S_')
    config.participant_id = id_textbox.get("1.0",'end-1c')
    config.freetext = freetext.get("1.0",'end-1c')

    #alien1 = canvas.create_oval(20 + 90, 260 - 130, 40 + 90, 300 - 130, outline='white', fill='blue')
    canvas.itemconfigure(alien1, fill='blue')
    canvas.coords(alien1, 20+90, 260-130, 40+90, 300-130)

    guidance = 0
    config.timestr = getCurrentTimestamp()

    config.guidanceMode = "None"
    duration = 0  # i.e. wait for stop button
    # run in a thread with queue in order to get returned values
    recThread = Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(threadHandler.startRecordThread(arg1, arg2, arg3, arg4)), args=(que, midiFileLocation, guidance, duration, root))
    recThread.start()

def stopRecording():
    #config.waitThread.event.set()
    threadHandler.recordingFinished()
    config.stopButton["state"] = "disabled"

def load_songs():
    for k in range(10):
        Button(root,  text='Song ' + str(k+1), command=lambda k=k: loadSong(k+1)).place(x=30, y=k*60+30, height=50, width=200)

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
    while track == 0:
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
    global bpmSelected, playButton, playAfterButton, playAloneButton, connectButton
    global id_textbox, freetext
    global midiInputPort, midiOutputPort
    global alien1
    playButton = Button(root, text='Play Together', command=lambda: nextTask(1))
    playButton.place(x=675, y=440, height=50, width=150)
    playButton["state"] = "disabled"

    playAfterButton = Button(root, text='Play After', command=lambda: nextTask(0))
    playAfterButton.place(x=850, y=440, height=50, width=150)
    playAfterButton["state"] = "disabled"

    playAloneButton = Button(root, text='Play Alone', command=nextTaskAlone)
    playAloneButton.place(x=1025, y=440, height=50, width=150)
    playAloneButton["state"] = "disabled"

    config.stopButton = Button(root, text='Stop recording', command=stopRecording)
    config.stopButton.place(x=1200, y=440, height=50, width=150)
    config.stopButton["state"] = "disabled"

    alien1 = canvas.create_oval(20+90, 260-130, 40+90, 300-130, outline='white', fill='white')
    canvas.pack()

    Button(root, text='Quit', command=quit).place(x=1200, y=20, height=30, width=150)

    id_textbox = Text(root, bg="white", relief=GROOVE, bd=1)
    id_textbox.place(x=1200, y=70, height=25, width=150)
    id_textbox.insert(INSERT, "Enter ID")

    freetext = Text(root, bg="white", relief=GROOVE, bd=1)
    freetext.place(x=1200, y=110, height=60, width=150)
    freetext.insert(INSERT, "Free text")

    connectButton = Button(root, text='Connect', command=connectToMidi)
    connectButton.place(x=230, y = 640, height=50, width=200)
    connectButton["state"] = "disabled"

    Button(root, text='Refresh MIDI', command=refreshMidi).place(x=30, y = 640, height=50, width=200)

    bpms = [0] * (131-50)

    for bpm in range(50, 131):
        bpms[bpm-50] = str(bpm)

    bpmSelected = StringVar(root)
    bpmSelected.set('60')

    bpmPopup = OptionMenu(root, bpmSelected, *bpms).place(x=1200, y=120+100-45, height=50, width=150)

    refreshMidi()

    midiInputPort, inputs_midi = getMidiInputs()
    midiOutputPort, outputs_midi = getMidiOutputs()

    if len(inputs_midi)>0 and len(outputs_midi)>0:
        print("setting state to normal")
        connectButton["state"] = "normal"

def connectToMidi():
    global songNum, midiConnected, playButton, playAfterButton, playAloneButton
    print("Connect to midi input: " + midiInputPort.get())
    result_input = threadHandler.set_inport(midiInputPort.get())

    print("Connect to midi output: " + midiOutputPort.get())
    result_output = threadHandler.set_outport(midiOutputPort.get())

    if result_input and result_output:
        midiConnected = 1

    if songNum and midiConnected:
        playButton["state"] = "normal"
        playAfterButton["state"] = "normal"
        playAloneButton["state"] = "normal"


def refreshMidi():
    global midiInputPort, midiInputPopupMenu, midiOutputPort, midiOutputPopupMenu
    midiInputPort, inputs_midi = getMidiInputs()
    MidiInputPopupMenu = OptionMenu(root, midiInputPort, *inputs_midi).place(x=30, y=680, height=50, width=200)

    midiOutputPort, outputs_midi = getMidiOutputs()
    MidiOutputPopupMenu = OptionMenu(root, midiOutputPort, *outputs_midi).place(x=230, y=680, height=50, width=200)

def getMidiInputs():
    outputs_midi, inputs_midi  = get_midi_interfaces()
    midiInputPort = StringVar(root)
    if len(inputs_midi) == 0:
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

# Load a song (generate the midi file and the sheet music)
def loadSong(songNumSelected):
    global midiFileLocation, songNum, generatedBpm, playButton, playAfterButton, playAloneButton
    bpm = int(bpmSelected.get())
    print("Song "  + str(songNumSelected) + " pressed, bpm = " + str(bpm))
    # Create a midi file at the appropriate bpm
    makesongsly.make_song(songNumSelected, bpm)
    generatedBpm = bpm
    # use lilypad to make the sheet music  + midi
    load_notesheet('songs/song' + str(songNumSelected) + '.png')
    midiFileLocation = 'songs/song' + str(songNumSelected) + '.midi'
    songNum = songNumSelected

    if songNum and midiConnected:
        playButton["state"] = "normal"
        playAfterButton["state"] = "normal"
        playAloneButton["state"] = "normal"

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
subprocess.run(['mkdir', '-p', config.tempDir], stderr=subprocess.DEVNULL)
# Create a window and title
root = Tk()
root.title("Piano capture")
canvas = Canvas(root, width=750, height = 800, bg='white')
#canvas2 = Canvas(root, width = 300, height = 300)
#canvas2.pack()
piano_img = ImageTk.PhotoImage(Image.open("piano_notes_crop.png"))
canvas.create_image(110, 500, anchor=NW, image=piano_img)
#Notes.create_visual_notes(canvas)
hand_img = ImageTk.PhotoImage(Image.open("finger-positioning-on-piano-crop.png"))
canvas.create_image(380, 500, anchor=NW, image=hand_img)
#deleteOldFiles()

# initialize keyboard input and output threads
threadHandler.initInputThread()
threadHandler.initOutputThread(root)

load_Startmenu()
load_songs()
# Set the resolution of window
root.geometry("1500x1000")

root.mainloop()
