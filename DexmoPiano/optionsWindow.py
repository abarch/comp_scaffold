from tkinter import *


class optionsWindowClass():

    def __init__(self, root, guidanceModeList, bpm, maxNoteperBar, numberOfBars, guidanceMode, noteValuesList, pitchesList):
        self.root = root
        self.guidanceModeList = guidanceModeList
        self.bpm = bpm
        self.maxNoteperBar = maxNoteperBar
        self.numberOfBars = numberOfBars
        self.guidanceMode = guidanceMode
        self.noteValuesList = noteValuesList
        self.pitchesList = pitchesList

    # create Window to specify next task, root waiting until this window is closed
    def changeParameter(self):

        self.specifyWindow = Toplevel(master = self.root)

        self.specifyWindow.transient(self.root)
        self.specifyWindow.grab_set()
        self.specifyWindow.geometry("310x540")
        self.specifyWindow.title("Options for next task")

    ## NOTEVALUE checkboxes
        l1 = Label(self.specifyWindow, text=" Notevalues:")
        l1.grid (row=1,columnspan=4,sticky=W, pady=(20,0))

        global fullNote, halfNote, quarterNote, eighthNote, sixteenthNote

        fullNote = BooleanVar()
        fullNote.set(1 in self.noteValuesList)
        chk1 = Checkbutton(self.specifyWindow, text='1', var=fullNote)
        chk1.grid(column=1, row=2)

        halfNote = BooleanVar()
        halfNote.set(1/2 in self.noteValuesList)
        chk1_2 = Checkbutton(self.specifyWindow, text='1/2', var=halfNote)
        chk1_2.grid(column=2, row=2)

        quarterNote = BooleanVar()
        quarterNote.set(1/4 in self.noteValuesList)
        chk1_4 = Checkbutton(self.specifyWindow, text='1/4', var=quarterNote)
        chk1_4.grid(column=3, row=2)

        eighthNote = BooleanVar()
        eighthNote.set(1/8 in self.noteValuesList)
        chk1_8 = Checkbutton(self.specifyWindow, text='1/8', var=eighthNote)
        chk1_8.grid(column=4, row=2)

        sixteenthNote = BooleanVar()
        sixteenthNote.set(1/16 in self.noteValuesList)
        chk1_16 = Checkbutton(self.specifyWindow, text='1/16', var=sixteenthNote)
        chk1_16.grid(column=5, row=2)

    ## Max notes per bar
        l2 = Label(self.specifyWindow, text=" Maximal note number per bar:")
        l2.grid(row=3,columnspan=4, sticky=W, pady=(20,0))

        OptionList = ["1","2","3","4"]
        maxNoteNumber = StringVar(self.specifyWindow)
        maxNoteNumber.set(self.maxNoteperBar)

        opt = OptionMenu(self.specifyWindow, maxNoteNumber, *OptionList)
        opt.grid(row=4,columnspan=4,sticky=W,)

    ## Number of Bars
        l3 = Label(self.specifyWindow, text=" Number of bars:")
        l3.grid(row=5,columnspan=4, sticky=W, pady=(20,0))

        numberBars = Scale(self.specifyWindow, from_=2, to=30, orient=HORIZONTAL)
        numberBars.grid(row=6, columnspan=4,sticky=W,)
        numberBars.set(self.numberOfBars)

    ## Beats per minute
        l4 = Label(self.specifyWindow, text=" Beats per minute:")
        l4.grid(row=7,columnspan=4, sticky=W, pady=(20,0))

        bpmscale = Scale(self.specifyWindow, from_=60, to=200, orient=HORIZONTAL)
        bpmscale.grid(row=8, columnspan=4,sticky=W,)
        bpmscale.set(self.bpm)

    ## NOTEPITCHES checkboxes
        l5 = Label(self.specifyWindow, text=" Notepitches:")
        l5.grid (row=9,columnspan=4,sticky=W, pady=(20,0))

        global C, D, E, F, G, A, B, C5

        C = BooleanVar()
        C.set(60 in self.pitchesList)
        c1 = Checkbutton(self.specifyWindow, text='C', var=C)
        c1.grid(column=1, row=10)

        D = BooleanVar()
        D.set(62 in self.pitchesList)
        d1 = Checkbutton(self.specifyWindow, text='D', var=D)
        d1.grid(column=2, row=10)

        E = BooleanVar()
        E.set(64 in self.pitchesList)
        e1 = Checkbutton(self.specifyWindow, text='E', var=E)
        e1.grid(column=3, row=10)

        F = BooleanVar()
        F.set(65 in self.pitchesList)
        f1 = Checkbutton(self.specifyWindow, text='F', var=F)
        f1.grid(column=4, row=10)

        G = BooleanVar()
        G.set(67 in self.pitchesList)
        g1 = Checkbutton(self.specifyWindow, text='G', var=G)
        g1.grid(column=5, row=10)

        A = BooleanVar()
        A.set(69 in self.pitchesList)
        a1 = Checkbutton(self.specifyWindow, text='A', var=A)
        a1.grid(column=1, row=11)

        B = BooleanVar()
        B.set(71 in self.pitchesList)
        b1 = Checkbutton(self.specifyWindow, text='B', var=B)
        b1.grid(column=2, row=11)

        C5 = BooleanVar()
        C5.set(72 in self.pitchesList)
        c5 = Checkbutton(self.specifyWindow, text='C5', var=C5)
        c5.grid(column=3, row=11)

    ## Max notes per bar
        l6 = Label(self.specifyWindow, text=" Guidance mode:")
        l6.grid(row=12,columnspan=4, sticky=W, pady=(20,0))

    ## Guidance options
        guidance = StringVar(self.specifyWindow)
        guidance.set(self.guidanceMode)
        guideopt = OptionMenu(self.specifyWindow, guidance, *self.guidanceModeList)
        guideopt.grid(row=13,columnspan=6,sticky=W,)


    ## Save and quit button
        l7 = Label(self.specifyWindow, text=" \n \n ")
        l7.grid(row=14,columnspan=4, sticky=W)

        saveButton = Button(self.specifyWindow, text ='Save and quit',
                            command =lambda: self.save_settings(saveBPM=bpmscale.get(), saveBarNumber=numberBars.get(),
                                                                saveNotesPerBar=maxNoteNumber.get(), saveGuidance=guidance.get()))
        saveButton.grid(row= 15, column = 4, columnspan = 3, pady=(20,0))

        quitButton = Button(self.specifyWindow, text ='Quit without saving',command =lambda: self.quit_options())
        quitButton.grid(row= 15, columnspan = 3, pady=(20,0))

        self.root.wait_window(self.specifyWindow)

    # get list of choosen notevalues
    def get_noteValues(self):
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

    # get list of choosen pitches
    def get_pitches(self):
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

    # show error if no pitch or no note value is choosen
    def show_empty_list_error(self):
        l7 = Label(self.specifyWindow, text=" Error: \n At least one pitch and one \n notevalue must be selected.",
             fg = "red")
        l7.grid(row=14,column = 2, columnspan=4, sticky=W)

    # save settings to generate a new task with it
    def save_settings(self, saveBPM, saveBarNumber, saveNotesPerBar, saveGuidance):
        if not self.get_noteValues() or not self.get_pitches():
            self.show_empty_list_error()
        else:
            self.bpm = saveBPM
            self.numberOfBars = saveBarNumber
            self.maxNoteperBar = int(saveNotesPerBar)
            self.guidanceMode = saveGuidance
            self.noteValuesList = self.get_noteValues()
            self.pitchesList = self.get_pitches()
            self.specifyWindow.destroy()
            if (self.guidanceMode == "At every note (note C-G)"):
                # remove A, B, C5 to have only five notes for domputeing finger numbers easily
                unwanted= {69,71,72}
                self.pitchesList = [ele for ele in self.pitchesList if ele not in unwanted]

    # quit options window without saving settings
    def quit_options(self):
        self.specifyWindow.destroy()

    # return all choosen options to main
    def get_data(self):
        return self.bpm, self.numberOfBars, self.maxNoteperBar, self.guidanceMode, self.noteValuesList, self.pitchesList
