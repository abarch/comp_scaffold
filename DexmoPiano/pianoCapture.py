from tkinter import *
from PIL import Image, ImageTk
import subprocess
import os
import mido
import makesongsly
import time
# import visualNotes
from threading import Thread
import datetime
import threadHandler
import queue
import config
import sys
import csv
import glob
from visualNotes import VisualNotes
import serial
import serial.tools.list_ports

midiFileLocation = ''
midiInputPort = ''
midiOutputPort = ''
midiPopupMenu = 0
midiInputPopupMenu = 0
midiOutputPopupMenu = 0
midiConnected = 0

songNames = []
songFiles = []
songButtons = []
piano_img = []
panel = []
songName = ''  # which song to play
songFile = ''  # filename of current song
generatedBpm: int = 0  # bpm to play the song back at

midiSaved = False  # Indicates if the output file was already created


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
def nextTask(finishAfterSong, userSelectedTask=False, userSelectedLocation=config.inputFileStrs[0]):
    global midiFileLocation, midiSaved, alien1, generatedBpm, bpmSelected, songFile

    bpm = int(bpmSelected.get())

    config.playMode = "tempo"

    # If the bpm has changed since the midi file was generated, regenerate
    if bpm != generatedBpm:
        makesongsly.make_song(songFile, bpm)

    que = queue.Queue()
    config.str_date = datetime.datetime.today().strftime('_%Y_%m_%d_%H_%M_%S_')
    config.participant_id = id_textbox.get("1.0", 'end-1c')
    config.freetext = freetext.get("1.0", 'end-1c')
    # alien1 = canvas.create_oval(20 + 90, 260 - 130, 40 + 90, 300 - 130, outline='white', fill='blue')
    # canvas.itemconfigure(alien1, fill='blue')
    # canvas.coords(alien1,20+90 , 260-130 , 40+90 , 300 -130)

    guidance = 0
    config.timestr = getCurrentTimestamp()
    config.playing_start_time = time.time()
    config.guidanceMode = "None"

    # run the animation. for some reason it is delayed when using join() later.. TBD:FIX
    if showScoreGuidance.get():
        config.vnotes.set_mode("cont")  # set visual notes mode to continuous drawing
        config.vnotes.clear_notes()
        cursorThread = Thread(target=animate_keyboard)
        cursorThread.start()

    # run in a thread with queue in order to get returned values
    recPlayThread = Thread(target=lambda q, arg1, arg2, arg3, arg4: q.put(threadHandler.startThreadsPianoCapture(arg1, arg2, arg3, arg4)),
                           args=(que, midiFileLocation, guidance,None, finishAfterSong))

    # run the thread
    recPlayThread.start()

# wait until an external trigger (via a Serial port) is received
def nextTaskExternalTrigger():
    # Turn off the other buttons
    config.waitButton["state"] = "disabled"
    config.playButton["state"] = "disabled"
    config.playAfterButton["state"] = "disabled"
    config.playAloneButton["state"] = "disabled"
    config.playOnExternalTriggerButton["state"] = "disabled"

    # wait for a trigger, then call nextTaskAlone
    waitForTriggerCOM()
    print('Trigger received, starting MIDI recording')
    nextTaskAlone('cont')

# don't play the song - wait until the stop button is pressed
def nextTaskAlone(mode, userSelectedTask=False, userSelectedLocation=config.inputFileStrs[0]):
    global midiFileLocation, midiSaved, alien1, generatedBpm

    # Turn on the stop button
    config.stopButton["state"] = "active"
	# Turn off the other buttons
    config.waitButton["state"] = "disabled"
    config.playButton["state"] = "disabled"
    config.playAfterButton["state"] = "disabled"
    config.playAloneButton["state"] = "disabled"
    config.playOnExternalTriggerButton["state"] = "disabled"


    # force a redraw
    root.update()

    bpm = int(bpmSelected.get())

    # If the bpm has changed since the midi file was generated, regenerate
    if songName and (bpm != generatedBpm):
        makesongsly.make_song(songName, bpm)

    que = queue.Queue()
    config.str_date = datetime.datetime.today().strftime('_%Y_%m_%d_%H_%M_%S_')
    config.participant_id = id_textbox.get("1.0", 'end-1c')
    config.freetext = freetext.get("1.0", 'end-1c')

    # alien1 = canvas.create_oval(20 + 90, 260 - 130, 40 + 90, 300 - 130, outline='white', fill='blue')
    # canvas.itemconfigure(alien1, fill='blue')
    # canvas.coords(alien1, 20+90, 260-130, 40+90, 300-130)

    guidance = 0
    config.timestr = getCurrentTimestamp()

    config.guidanceMode = "None"
    duration = 0  # i.e. wait for stop button
    # run in a thread with queue in order to get returned values

    config.playing_start_time = time.time()

    if showVerticalGuidance.get():
        config.vnotes.set_mode(mode)
        config.vnotes.clear_notes()
    if mode == "cont":
        if showScoreGuidance.get():
            cursorThread = Thread(target=animate_keyboard)
            cursorThread.start()
    elif mode == "wait":
        if showVerticalGuidance.get():
            config.vnotes.init_wait_for_note()

    recThread = Thread(
        target=lambda q, arg1, arg2, arg3, arg4: q.put(threadHandler.startRecordThread(arg1, arg2, arg3, arg4)),
        args=(que, midiFileLocation, guidance, duration, root))
    recThread.start()
	
    if COMport.get() != 'None':
        sendTriggerCOM("1")
	

def sendTriggerCOM(message):
    global serialPort
    serialPort.write(bytes(message, encoding='utf8'))
    print('Sent trigger ' + message + ' on COM port ' + COMport.get())

# This will freeze the program until the serial trigger is received (after clearing the buffer)
def waitForTriggerCOM():
    while(serialPort.in_waiting > 0):
        serialPort.read(serialPort.in_waiting)
    while(1):
        if(serialPort.in_waiting > 0):
            data = serialPort.read(1)
            print('Received' + str(data))
            break

def stopRecording():
    # config.waitThread.event.set()
    threadHandler.recordingFinished()
    config.stopButton["state"] = "disabled"
    config.waitButton["state"] = "active"
    config.playButton["state"] = "active"
    config.playAfterButton["state"] = "active"
    config.playAloneButton["state"] = "active"
    config.playOnExternalTriggerButton["state"] = "active"

	
    if COMport.get() != 'None':
        sendTriggerCOM("0")


def load_songlist(filename):
    global songNames, songFiles
    
    if not os.path.exists(filename):
        print("Song list file " + songlist + " does not exist, exiting")
        exit()
    print('Using song list file: ' + filename)
    count = 0
    if songButtons:
        for button in songButtons:
            button.destroy()
    songNames = []
    songFiles = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            count = count + 1
            if count > 10:
                print("Maximum 10 songs, ignoring rest")
                break
            songNames.append(row[0])
            songFiles.append(row[1])
    load_songs()


def load_songs():
    global songButtons
    for k in range(len(songNames)):
        b = Button(root, wraplength=200, text=songNames[k], fg='blue', command=lambda k=k: loadSong(songFiles[k], songNames[k]))
        b.place(x=30, y=k * 50 + 110, height=40, width=200)
        songButtons.append(b)

def movement():
    global alien1
    # This is where the move() method is called
    # This moves the rectangle to x, y coordinates

    print("move.")
    #   canvas.move(alien1, 5, 0)
    #  canvas.pack()
    # canvas.draw() not working
    canvas.after(1, movement)


def animate_keyboard():
    global bpmSelected

    bpm = int(bpmSelected.get())
    bars = 8
    song_length_pixels = 123 * 5
    correction = 50
    track = 0
    dx = 1
    while track == 0:
        for i in range(0, 123 * 5):
            # if config.noteStatus:
            config.vnotes.update_actual_notes(time.time() - config.playing_start_time)
            print(i)
            # print(config.vnotes.is_wait_for_note_done())
            # else:
            #   config.vnotes.update_key_released(60,3)
            # print( )
            time.sleep(60.0 * 4 * bars * dx / ((song_length_pixels + correction) * bpm))
        track = 1
    print("check")
    print(track)


def animation_test():
    global bpmSelected

    bpm = int(bpmSelected.get())
    bars = 8
    song_length_pixels = 123 * 5
    correction = 50
    track = 0
    dx = 1
    while track == 0:
        for i in range(0, 123 * 5):
            # if config.noteStatus:
            # config.vnotes.update_actual_notes(time.time()-config.playing_start_time)
            print(config.vnotes.is_wait_for_note_done())
            # else:
            #   config.vnotes.update_key_released(60,3)
            # print(config.pitchPressed)
            time.sleep(60.0 * 4 * bars * dx / ((song_length_pixels + correction) * bpm))
        track = 1
    print("check")
    print(track)


# load start menu with button for first task and exit button
def load_Startmenu():
    global bpmSelected, connectButton
    global showScoreGuidance, showVerticalGuidance, showNotes1, showNotes2, canvas, piano_img, hand_img
    global id_textbox, freetext
    global midiInputPort, midiOutputPort, COMport
    global alien1

    canvas = Canvas(root, width=800, height=800, bg='white')
    #canvas.pack()
    canvas.place(x=260, y=20)

    config.waitButton = Button(root, text='Wait for Note', command=lambda: nextTaskAlone('wait'))
    config.waitButton.place(x=1120, y=500, height=50, width=150)
    config.waitButton["state"] = "disabled"

    config.playButton = Button(root, text='Play Together', command=lambda: nextTask(1))
    config.playButton.place(x=1280, y=500, height=50, width=150)
    config.playButton["state"] = "disabled"

    config.playAfterButton = Button(root, text='Play After', command=lambda: nextTask(0))
    config.playAfterButton.place(x=1120, y=560, height=50, width=150)
    config.playAfterButton["state"] = "disabled"

    config.playAloneButton = Button(root, text='Play Alone', command=lambda: nextTaskAlone('cont'))
    config.playAloneButton.place(x=1280, y=560, height=50, width=150)
    config.playAloneButton["state"] = "disabled"

    config.playOnExternalTriggerButton = Button(root, text='Play on External Trigger', command=lambda: nextTaskExternalTrigger())
    config.playOnExternalTriggerButton.place(x=1280, y=620, height=50, width=150)
    config.playOnExternalTriggerButton["state"] = "disabled"

    config.stopButton = Button(root, text='Stop recording', command=stopRecording)
    config.stopButton.place(x=1120, y=620, height=50, width=150)
    config.stopButton["state"] = "disabled"

    # alien1 = canvas.create_oval(20+90, 260-130, 40+90, 300-130, outline='white', fill='white')

    Button(root, text='Quit', command=quit).place(x=1200, y=20, height=30, width=150)

    id_textbox = Text(root, bg="white", fg="black", relief=GROOVE, bd=1, state=NORMAL)
    id_textbox.place(x=1200, y=70, height=25, width=150)
    id_textbox.insert(INSERT, "Enter ID")

    freetext = Text(root, bg="white", fg="black", relief=GROOVE, bd=1)
    freetext.place(x=1200, y=110, height=60, width=150)
    freetext.insert(INSERT, "Free text")

    showScoreGuidance = IntVar(value=0)
    showScoreGuidanceCheck = Checkbutton(root, text='Show score guidance', variable=showScoreGuidance,
                                         command=updateGuidance)
    showScoreGuidanceCheck.place(x=1200, y=250, height=50, width=200)

    showVerticalGuidance = IntVar(value=0)
    showVerticalGuidanceCheck = Checkbutton(root, text='Show vertical guidance', variable=showVerticalGuidance,
                                            command=updateGuidance)
    showVerticalGuidanceCheck.place(x=1200, y=300, height=50, width=200)
    config.showVerticalGuidance = showVerticalGuidance.get()

    showNotes1 = IntVar(value=0)
    showNotes1Check = Checkbutton(root, text='Show notes guidance (left)', variable=showNotes1,
                                  command=updateGuidance)
    showNotes1Check.place(x=1200, y=350, height=50, width=200)

    showNotes2 = IntVar(value=0)
    showNotes2Check = Checkbutton(root, text='Show notes guidance (right)', variable=showNotes2,
                                  command=updateGuidance)
    showNotes2Check.place(x=1200, y=400, height=50, width=200)

    Button(root, text='Refresh MIDI', command=refreshMidi).place(x=30, y=620, height=50, width=200)

    connectButton = Button(root, text='Connect', command=connectToMidi)
    connectButton.place(x=30, y=680, height=50, width=200)
    connectButton["state"] = "disabled"


    bpms = [0] * (131 - 50)

    for bpm in range(50, 131):
        bpms[bpm - 50] = str(bpm)

    bpmSelected = StringVar(root)
    bpmSelected.set('60')

    bpmPopup = OptionMenu(root, bpmSelected, *bpms).place(x=1200, y=120 + 100 - 45, height=50, width=150)

    piano_img = ImageTk.PhotoImage(Image.open("piano_notes_crop.png"))
    canvas.create_image(200, 300, anchor=NW, image=piano_img)

    hand_img = ImageTk.PhotoImage(Image.open("finger-positioning-on-piano-crop.png"))
    canvas.create_image(470, 300, anchor=NW, image=hand_img)

    updateGuidance()

    songbooks = []
    for file in glob.glob("*.csv"):
        songbooks.append(file)

    songbook = StringVar(root)
    songbook.set("defaultSongs.csv")

    songbookPopupMenu = OptionMenu(root, songbook, *songbooks, command = load_songlist).place(x=30, y=10, height=40, width=200)

    Button(root, wraplength=200, text='Blank score', fg='red', command=loadBlank).place(x=30, y=60, height=40, width=200)

    ports = serial.tools.list_ports.comports()
    COMports = []
    COMports.append('None')
    for port, desc, hwid in sorted(ports):
        COMports.append(port)
    COMport = StringVar(root)
    COMport.set(COMports[0])
    COMportMenu = OptionMenu(root, COMport, *COMports).place(x=30, y=770, height=20, width=230)
	
    midiInputPort, inputs_midi = getMidiInputs()
    midiOutputPort, outputs_midi = getMidiOutputs()

    refreshMidi()

    if len(inputs_midi) > 0 and len(outputs_midi) > 0:
        print("setting state to normal")
        connectButton["state"] = "normal"


def updateGuidance():
    global showNotes1, showNotes2, showScoreGuidance, showVerticalGuidance, canvas, piano_img, hand_img

    config.showVerticalGuidance = showVerticalGuidance.get()

    if showVerticalGuidance.get() == 0:
        canvas.create_rectangle(0, 200, 500, 600, fill='white', outline='white')
    else:
        setupVisualNotes()

    if showNotes1.get() == 0:
        canvas.create_rectangle(200, 300, 200+264-1, 300+219-1, fill='white', outline='white')
    else:
        canvas.create_image(200, 300, anchor=NW, image=piano_img)

    if showNotes2.get() == 0:
        canvas.create_rectangle(470, 300, 470+277-1, 300+277-1, fill='white', outline='white')
    else:
        canvas.create_image(470, 300, anchor=NW, image=hand_img)



def connectToMidi():
    global songName, midiConnected, COMport, serialPort
    print("Connect to midi input: " + midiInputPort.get())
    result_input = threadHandler.set_inport(midiInputPort.get())

    print("Connect to midi output: " + midiOutputPort.get())
    result_output = threadHandler.set_outport(midiOutputPort.get())

    # Also connect to serial port
    thisCOMport = COMport.get()
    if thisCOMport=='None':
        print('No COM port selected so not connecting')
    else:
        serialPort = serial.Serial(
			port=thisCOMport, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
        )
        print('Connected to ' + thisCOMport)

    if result_input and result_output:
        midiConnected = 1

    if midiConnected:
        config.waitButton["state"] = "normal"
        config.playButton["state"] = "normal"
        config.playAfterButton["state"] = "normal"
        config.playAloneButton["state"] = "normal"
        config.playOnExternalTriggerButton["state"] = "normal"


def refreshMidi():
    global midiInputPort, midiInputPopupMenu, midiOutputPort, midiOutputPopupMenu
    midiInputPort, inputs_midi = getMidiInputs()
    MidiInputPopupMenu = OptionMenu(root, midiInputPort, *inputs_midi).place(x=30, y=730, height=20, width=200)

    midiOutputPort, outputs_midi = getMidiOutputs()
    MidiOutputPopupMenu = OptionMenu(root, midiOutputPort, *outputs_midi).place(x=30, y=750, height=20, width=200)

def getMidiInputs():
    global midiInputPopupMenu
    outputs_midi, inputs_midi = get_midi_interfaces()
    midiInputPort = StringVar(root)
    if len(inputs_midi) == 0:
        midiInputPort.set('')
        inputs_midi = {''}
    else:
        midiInputPort.set(inputs_midi[midiInputPopupMenu])
    return midiInputPort, inputs_midi


def getMidiOutputs():
    global midiOutputPopupMenu
    outputs_midi, inputs_midi = get_midi_interfaces()
    midiOutputPort = StringVar(root)
    if len(outputs_midi) == 0:
        midiOutputPort.set('')
        outputs_midi = {''}
    else:
        midiOutputPort.set(outputs_midi[midiOutputPopupMenu])
    return midiOutputPort, outputs_midi

# Load a blank score
def loadBlank():
    global background, panel
    # Set free text to blank
    freetext.delete("1.0", "end-1c")
    freetext.insert(END, "blank")
    config.freetext = "blank"
    if panel:
        panel.destroy()

# Load a song (generate the midi file and the sheet music)
def loadSong(thisSongFile, thisSongName):
    global midiFileLocation, songName, songFile, generatedBpm
    bpm = int(bpmSelected.get())
    print("Loading " + thisSongFile + ", bpm = " + str(bpm))
    # Set free text to name of song
    freetext.delete("1.0", "end-1c")
    freetext.insert(END, thisSongName)
    config.freetext = thisSongName
    # Create a midi file at the appropriate bpm
    makesongsly.make_song(thisSongFile, bpm)
    generatedBpm = bpm
    # use lilypad to make the sheet music  + midi
    load_notesheet('songs/' + thisSongFile + '.png')
    midiFileLocation = 'songs/' + thisSongFile + '.midi'
    songName = thisSongName
    songFile = thisSongFile

    if songName and midiConnected:
        config.waitButton["state"] = "normal"
        config.playButton["state"] = "normal"
        config.playAfterButton["state"] = "normal"
        config.playAloneButton["state"] = "normal"
        config.playOnExternalTriggerButton["state"] = "normal"


# loads notesheet for actual task
def load_notesheet(png):
    global background, panel
    if panel:
        panel.destroy()

    background = Image.open(png)
    background = background.convert("RGBA")
    width, height = background.size

    img = ImageTk.PhotoImage(background)
    panel = Label(root, image=img)
    panel.image = img
    panel.option_clear()
    panel.place(x=260, y=30, width=width, height=height)


def get_midi_interfaces():
    return mido.get_output_names(), mido.get_input_names()

def setupVisualNotes():
    global canvas
    config.vnotes = VisualNotes(canvas=canvas, start_pos_x=30, start_pos_y=200, quarter_len=12)
    config.vnotes.set_mode("cont")
    config.vnotes.draw_keyboard(False)
    config.vnotes.init_v_cursor()
    config.vnotes.init_h_cursor(20 + 90, 260 - 130, 20)
    config.vnotes.set_tempo(60)
    pitch_list, duration_list = config.vnotes.create_pitch_duration_lists("c2 c e e c c e e g g e e c c c1")
    config.vnotes.set_notes(pitch_list, duration_list)
    config.vnotes.draw_notes()


# program starts here

# create file output folder if it does not already exist
if not os.path.isdir(config.tempDir):
	os.mkdir(config.tempDir)
# Create a window and title
songlist = 'defaultsongs.csv'
if len(sys.argv) > 1:  # i.e., no arguments
    songlist = sys.argv[1]

root = Tk()
root.title("Piano capture")
load_Startmenu()

# Load the songs list
load_songlist(songlist)


# deleteOldFiles()

#setupVisualNotes()

# initialize keyboard input and output threads
threadHandler.initInputThread()
threadHandler.initOutputThread(root)


# Set the resolution of window
root.geometry("1500x850")

root.mainloop()
