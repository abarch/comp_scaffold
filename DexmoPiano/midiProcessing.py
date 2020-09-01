from midiutil.MidiFile import MIDIFile

import copy
import os
import random

import pianoplayer_interface


# some code taken from https://github.com/Michael-F-Ellis/tbon
class MidiProcessing:
    ### CONSTANTS ###
    CHANNEL_PIANO = 0
    CHANNEL_METRO = 9
    CHANNEL_LH = 11
    CHANNEL_RH = 10

    INSTRUM_PIANO = 0
    INSTRUM_DRUMS = 9
    INSTRUM_DEXMO = 0

    PITCH_METRO_HI = 76  # high wood block
    PITCH_METRO_LO = 77  # low wood block
    VOLUME = 100
    TIME = 0  # start at the beginning

    INTRO_BARS = 1  # no. of empty first bars for metronome intro
    ACROSS_BARS = 0  # allow notes to reach across two bars

    # time signature (ex. 4/4 = (4, 4))
    # TODO: USE AS INPUT?
    timeSig = (4, 4)

    # outFiles: [midi, midi+metronome, midi+metronome+dexmo, musicXML)
    def __init__(self, left, right, bpm, outFiles):
        self.bpm = bpm
        self.left = left
        self.right = right
        self.outFiles = outFiles

        if left and right:
            self.r_track = 0  # right hand track
            self.l_track = 1  # left hand track
            self.m_track = 2  # metronome track
            self.rd_track = 3  # right hand dexmo track
            self.ld_track = 4  # left hand dexmo track
        elif left:
            self.l_track = 0  # left hand track
            self.m_track = 1  # metronome track
            self.ld_track = 2  # left hand dexmo track
        elif right:
            self.r_track = 0  # right hand track
            self.m_track = 1  # metronome track
            self.rd_track = 2  # right hand dexmo track

        self.mf = MIDIFile(numTracks=self.get_track_num())
        self.setup_midiFile()

    def get_track_num(self):
        if self.left and self.right:
            return 5
        else:
            return 3

    def setup_midiFile(self):
        if self.left:
            self.mf.addTrackName(self.l_track, self.TIME, "Left Hand")
            self.mf.addTrackName(self.ld_track, self.TIME, "Left Hand Dexmo")
        if self.right:
            self.mf.addTrackName(self.r_track, self.TIME, "Right Hand")
            self.mf.addTrackName(self.rd_track, self.TIME, "Right Hand Dexmo")
        self.mf.addTrackName(self.m_track, self.TIME, "Metronome")

        self.mf.addTempo(self.m_track, self.TIME,
                         self.bpm)  # in file format 1, track doesn't matter; changed to m because always added

    def set_time_signature(self, numerator, denominator):
        # map denominator to power of 2 for MIDI
        midiDenom = {2: 1, 4: 2, 8: 3, 16: 4}[denominator]
        # make the midi metronome match beat duration
        # (requires recognizing compound meters)
        if denominator == 16 and (numerator % 3 == 0):
            metro_clocks = 18
        elif denominator == 16:
            metro_clocks = 6
        elif denominator == 8 and (numerator % 3 == 0):
            metro_clocks = 36
        elif denominator == 8:
            metro_clocks = 12
        elif denominator == 4:
            metro_clocks = 24
        elif denominator == 2:
            metro_clocks = 48
        else:
            metro_clocks = 24

        self.mf.addTimeSignature(track=self.m_track,
                                 time=self.TIME,
                                 numerator=numerator,
                                 denominator=midiDenom,
                                 clocks_per_tick=metro_clocks)

    def write_midi(self, out_file):
        with open(out_file, 'wb') as outf:
            copy.deepcopy(self.mf).writeFile(outf)

    # fileList: [midi, midi+metronome, midi+metronome+dexmo, musicXML)
    ###TODO: Fix! Dexmo notes somehow get into the metronome-only file
    def generate_metronome_and_fingers_for_midi(self, fileList, noOfBars):
        numerator, denominator = self.timeSig

        self.set_time_signature(numerator, denominator)
        sf = self.generate_fingers_and_write_xml(fileList[0], fileList[3], noOfBars)
        self.add_metronome(noOfBars + self.INTRO_BARS, numerator, fileList[1])
        self.add_fingernumbers(fileList[2], sf, True)

    def generateMidi(self, noteValues, notesPerBar, noOfBars, pitches):
        ### EXERCISE GENERATION ###

        numerator, denominator = self.timeSig

        # adjust no. of bars (in case of intro bars)
        bars = noOfBars + self.INTRO_BARS

        self.set_time_signature(numerator, denominator)

        ### CHOOSE TIMESTEPS ###

        timesteps = []
        minNoteVal = min(noteValues)

        # randomly generate the chosen number of timesteps (notes) per bar
        stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
        for bar in range(noOfBars - 1):			# last bar is for extra notes
            # determine no. of notes in this bar
            noOfNotes = random.choice(notesPerBar)

            # shift step numbers
            shift = (bar + self.INTRO_BARS) * numerator
            steps = [temp + shift for temp in stepRange]

            timesteps.append(random.sample(steps, noOfNotes))

        # flatten and sort list
        timesteps = sorted([item for sublist in timesteps for item in sublist])

        # append dummy element to avoid additional bar
        timesteps.append(bars * numerator)

        # print("timesteps:", timesteps[:-1])

        ### ADD PIANO NOTES ###

        # add music (piano) notes
        if self.right:
            self.mf.addProgramChange(self.r_track, self.CHANNEL_PIANO, self.TIME, self.INSTRUM_PIANO)
        if self.left:
            self.mf.addProgramChange(self.l_track, self.CHANNEL_PIANO, self.TIME, self.INSTRUM_PIANO)

        # custom for-loop
        t = 0
        while t < (len(timesteps) - 1):
            # compute maximum note length until next note
            maxNoteVal = (timesteps[t + 1] - timesteps[t]) / denominator
            ###temp = maxNoteVal

            # compute maximum note length until next bar
            if not self.ACROSS_BARS:
                maxToNextBar = 1 - ((timesteps[t] % denominator) / denominator)
                maxNoteVal = min([maxNoteVal, maxToNextBar])

            ###print(timesteps[t], "min(", temp, maxToNextBar, ") =", maxNoteVal)

            # calculate possible note values at current time step
            possNoteValues = [v for v in noteValues if v <= maxNoteVal]
            # if list is empty, increment time step by 1 and try again
            if not possNoteValues:
                print(t, timesteps[t], maxNoteVal)
                timesteps[t] = timesteps[t] + 1
                continue

            # TODO: multiply with timeSig[1] here (instead below) when not printing anymore
            duration = random.choice(possNoteValues)
            # print(duration, "\n")

            pitch = random.choice(pitches)

            # choose right/left hand, split at C4 (MIDI: pitch 60)
            if (self.left and not self.right) or (self.left and self.right and (pitch < 60)):
                handTrack = self.l_track
            elif self.right:
                handTrack = self.r_track

            # print("original note pitches: " + str(pitch))
            self.mf.addNote(track=handTrack,
                            channel=self.CHANNEL_PIANO,
                            pitch=pitch,
                            time=timesteps[t],
                            duration=denominator * duration,
                            volume=self.VOLUME)

            t += 1


        # add 3 extra notes for proper fingering numbers
        for t in range(3):
        	tempTime = ((bars - 1) * numerator) + t + 1
	        self.mf.addNote(track=handTrack,
				            channel=self.CHANNEL_PIANO,
				            pitch=pitch,
				            time=tempTime,
				            duration=1,
				            volume=self.VOLUME)

        # write 1st MIDI file (piano only)
        self.write_midi(self.outFiles[0])

        ### METRONOME ###
        self.add_metronome(bars, numerator, self.outFiles[1])

        ### FINGERNUMBERS ###
        sf = self.generate_fingers_and_write_xml(self.outFiles[0], self.outFiles[3], noOfBars)
        self.add_fingernumbers(self.outFiles[2], sf, False)

    def add_metronome(self, bars, numerator, outFile):
        # add metronome notes
        self.mf.addProgramChange(self.m_track, self.CHANNEL_METRO, self.TIME, self.INSTRUM_DRUMS)

        for t in range(bars * numerator):

            # decide if downbeat or 'other' note
            if (t % numerator) == 0:
                # first beat in bar
                pitch = self.PITCH_METRO_HI
            else:
                pitch = self.PITCH_METRO_LO

            self.mf.addNote(track=self.m_track,
                            channel=self.CHANNEL_METRO,
                            pitch=pitch,
                            time=t,
                            duration=1,
                            volume=self.VOLUME)

        # write 2nd MIDI file (with metronome)
        self.write_midi(outFile)

    def generate_fingers_and_write_xml(self, midiFile, mxmlFile, noOfBars):
        pianoplayer = pianoplayer_interface.PianoplayerInterface(midiFile)
        lbeam = 1
        if self.left and not self.right:
            lbeam = 0
        pianoplayer.generate_fingernumbers(self.left and not self.right, self.right and not self.left, 0, lbeam,
                                           noOfBars)
        # pianoplayer.generate_fingernumbers(False, False, 0, 1, noOfBars)
        pianoplayer.write_output(mxmlFile)
        return pianoplayer.get_score()

    def add_fingernumbers(self, outFile, sf, with_note):
        if self.right:
            self.mf.addProgramChange(self.rd_track, self.CHANNEL_RH, self.TIME, self.INSTRUM_DEXMO)
        if self.left:
            self.mf.addProgramChange(self.ld_track, self.CHANNEL_LH, self.TIME, self.INSTRUM_DEXMO)

        for note in sf.parts[0].notesAndRests:
            if self.right:
                if with_note:
                    self.add_note_to_midi(note, self.r_track, self.CHANNEL_PIANO)
                self.add_dexmo_note_to_midi(note, self.rd_track, self.CHANNEL_RH)
            else:
                if with_note:
                    self.add_note_to_midi(note, self.l_track, self.CHANNEL_PIANO)
                self.add_dexmo_note_to_midi(note, self.ld_track, self.CHANNEL_LH)
        if self.left and self.right:
            for note in sf.parts[1].notesAndRests:
                if with_note:
                    self.add_note_to_midi(note, self.l_track, self.CHANNEL_PIANO)
                self.add_dexmo_note_to_midi(note, self.ld_track, self.CHANNEL_LH)

        # write 3rd MIDI file (with dexmo notes)
        self.write_midi(outFile)

    def add_dexmo_note_to_midi(self, note, track, channel):
        if note.isNote:
            pitch = self.convert_note_to_dexmo_note(note)
            # print("add dexmo note: " + str(note) + " pitch: " + str(pitch))
            # print("dexmo pitch: " + str(pitch))
            if pitch is not None:
                self.mf.addNote(track=track,
                                channel=channel,
                                pitch=pitch,
                                time=note.offset,
                                duration=note.duration.quarterLength,
                                volume=self.VOLUME)

    def add_note_to_midi(self, note, track, channel):
        if note.isNote:
            # print("add note: " + str(note) + " pitch: " + str(note.pitch.ps) + " time: " + str(note.offset) +
            # " duration: " + str(note.duration.quarterLength))
            self.mf.addNote(track=track,
                            channel=channel,
                            pitch=int(note.pitch.ps),
                            time=note.offset,
                            duration=note.duration.quarterLength,
                            volume=self.VOLUME)

    def convert_note_to_dexmo_note(self, note):
        if len(note.articulations) == 0:
            # print("no fingernumber")
            return None
        finger = note.articulations[0].fingerNumber
        # print("finger: " + str(finger))
        if finger is 1:
            # thumb
            return 29
        elif finger is 2:
            # idx
            return 41
        elif finger is 3:
            # mid
            return 53
        elif finger is 4:
            # ring
            return 65
        elif finger is 5:
            # pinky
            return 77
        return None


if __name__ == "__main__":

    noOfBars = 30

    outFiles=["./output/output.mid", "./output/output-m.mid",
              "./output/output-md.mid", "./output/output.xml"]

    # create folder if it does not exist yet
    outDir = "./output/"
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    midProc = MidiProcessing(left=True, right=True, bpm=120, outFiles=outFiles)

    midProc.generateMidi(noteValues=[1, 1 / 2, 1 / 4, 1 / 8],
                          notesPerBar=[2],  # range
                          noOfBars=noOfBars,
                          pitches=list(range(52, 68)))
    #pitches=[48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72])

    # midProc.generate_metronome_and_fingers_for_midi('test_input/TripletsAndQuarters.mid', 8)
    #midProc.generate_metronome_and_fingers_for_midi(fileList=outFiles, noOfBars=noOfBars)
