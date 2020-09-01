from midiutil.MidiFile import MIDIFile

import copy
import os
import random

import pianoplayer_interface


# some code taken from https://github.com/Michael-F-Ellis/tbon

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

def write_midi(out_file, mf):
    with open(out_file, 'wb') as outf:
        copy.deepcopy(mf).writeFile(outf)

def generateMidi(noteValues, notesPerBar, noOfBars, pitches, bpm, left, right, outFiles):

   ## from init here: tracknumber, tempo etc

    if left and right:
        r_track = 0  # right hand track
        l_track = 1  # left hand track
        m_track = 2  # metronome track
        rd_track = 3  # right hand dexmo track
        ld_track = 4  # left hand dexmo track
    elif left:
        l_track = 0  # left hand track
        m_track = 1  # metronome track
        ld_track = 2  # left hand dexmo track
        r_track = None
        rd_track = None
    else:
        r_track = 0  # right hand track
        m_track = 1  # metronome track
        rd_track = 2  # right hand dexmo track
        l_track = None
        ld_track = None

    # get track number
    if left and right:
        track_num = 5
    else:
        track_num = 3

    mf = MIDIFile(numTracks=track_num)

    if left:
        mf.addTrackName(l_track, TIME, "Left Hand")
        mf.addTrackName(ld_track, TIME, "Left Hand Dexmo")
    if right:
        mf.addTrackName(r_track, TIME, "Right Hand")
        mf.addTrackName(rd_track, TIME, "Right Hand Dexmo")
    mf.addTrackName(m_track, TIME, "Metronome")

    mf.addTempo(m_track, TIME, bpm)  # in file format 1, track doesn't matter; changed to m because always added


    ### EXERCISE GENERATION ###

    numerator, denominator = timeSig

    # adjust no. of bars (in case of intro bars)
    bars = noOfBars + INTRO_BARS

    ## set time signature
    # map denominator to power of 2 for MIDI

    # make the midi metronome match beat duration
    midiDenom = {2: 1, 4: 2, 8: 3, 16: 4}[denominator]
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

    mf.addTimeSignature(track=m_track,
                        time=TIME,
                        numerator=numerator,
                        denominator=midiDenom,
                        clocks_per_tick=metro_clocks)

    ### CHOOSE TIMESTEPS ###

    timesteps = []
    minNoteVal = min(noteValues)

    # randomly generate the chosen number of timesteps (notes) per bar
    stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
    for bar in range(noOfBars - 1):			# last bar is for extra notes
        # determine no. of notes in this bar
        noOfNotes = random.choice(notesPerBar)

        # shift step numbers
        shift = (bar + INTRO_BARS) * numerator
        steps = [temp + shift for temp in stepRange]

        timesteps.append(random.sample(steps, noOfNotes))

    # flatten and sort list
    timesteps = sorted([item for sublist in timesteps for item in sublist])

    # append dummy element to avoid additional bar
    timesteps.append(bars * numerator)

    # print("timesteps:", timesteps[:-1])

    ### ADD PIANO NOTES ###

    # add music (piano) notes
    if right:
        mf.addProgramChange(r_track, CHANNEL_PIANO, TIME, INSTRUM_PIANO)
    if left:
        mf.addProgramChange(l_track, CHANNEL_PIANO, TIME, INSTRUM_PIANO)

    # custom for-loop
    t = 0
    while t < (len(timesteps) - 1):
        # compute maximum note length until next note
        maxNoteVal = (timesteps[t + 1] - timesteps[t]) / denominator
        ###temp = maxNoteVal

        # compute maximum note length until next bar
        if not ACROSS_BARS:
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
        if left and ((not right) or (pitch < 60)):
            handTrack = l_track
        else:
            handTrack = r_track

        # print("original note pitches: " + str(pitch))
        mf.addNote(track=handTrack,
                   channel=CHANNEL_PIANO,
                   pitch=pitch,
                   time=timesteps[t],
                   duration=denominator * duration,
                   volume=VOLUME)

        t += 1

    # add 3 extra notes for proper fingering numbers
    for t in range(3):
        tempTime = ((bars - 1) * numerator) + t + 1
        mf.addNote(track=handTrack,
                        channel=CHANNEL_PIANO,
                        pitch=pitch,
                        time=tempTime,
                        duration=1,
                        volume=VOLUME)

    # write 1st MIDI file (piano only)
    write_midi(outFiles[0], mf)

    ### METRONOME ###
    add_metronome(bars, numerator, outFiles[1], mf, m_track)

    ### FINGERNUMBERS ###
    sf = generate_fingers_and_write_xml(outFiles[0], outFiles[3], noOfBars, left, right)
    add_fingernumbers(outFiles[2], sf, False, right, left, mf, rd_track, ld_track, r_track, l_track)

def add_metronome(bars, numerator, outFile, mf, m_track):
    # add metronome notes
    mf.addProgramChange(m_track, CHANNEL_METRO, TIME, INSTRUM_DRUMS)

    for t in range(bars * numerator):

        # decide if downbeat or 'other' note
        if (t % numerator) == 0:
            # first beat in bar
            pitch = PITCH_METRO_HI
        else:
            pitch = PITCH_METRO_LO

        mf.addNote(track=m_track,
                        channel=CHANNEL_METRO,
                        pitch=pitch,
                        time=t,
                        duration=1,
                        volume=VOLUME)

    # write 2nd MIDI file (with metronome)
    write_midi(outFile, mf)

def generate_fingers_and_write_xml(midiFile, mxmlFile, noOfBars, left, right):
    pianoplayer = pianoplayer_interface.PianoplayerInterface(midiFile)
    lbeam = 1
    if left and not right:
        lbeam = 0
    pianoplayer.generate_fingernumbers(left and not right, right and not left, 0, lbeam,
                                       noOfBars)
    # pianoplayer.generate_fingernumbers(False, False, 0, 1, noOfBars)
    pianoplayer.write_output(mxmlFile)
    return pianoplayer.get_score()

def add_fingernumbers(outFile, sf, with_note, right, left, mf, rd_track, ld_track, r_track, l_track):
    if right:
        mf.addProgramChange(rd_track, CHANNEL_RH, TIME, INSTRUM_DEXMO)
    if left:
        mf.addProgramChange(ld_track, CHANNEL_LH, TIME, INSTRUM_DEXMO)

    for note in sf.parts[0].notesAndRests:
        if right:
            if with_note:
                add_note_to_midi(note, r_track, CHANNEL_PIANO, mf)
            add_dexmo_note_to_midi(note, rd_track, CHANNEL_RH, mf)
        else:
            if with_note:
                add_note_to_midi(note, l_track, CHANNEL_PIANO, mf)
            add_dexmo_note_to_midi(note, ld_track, CHANNEL_LH, mf)
    if left and right:
        for note in sf.parts[1].notesAndRests:
            if with_note:
                add_note_to_midi(note, l_track, CHANNEL_PIANO, mf)
            add_dexmo_note_to_midi(note, ld_track, CHANNEL_LH, mf)

    # write 3rd MIDI file (with dexmo notes)
    write_midi(outFile, mf)

def add_dexmo_note_to_midi(note, track, channel, mf):
    if note.isNote:
        pitch = convert_note_to_dexmo_note(note)
        # print("add dexmo note: " + str(note) + " pitch: " + str(pitch))
        # print("dexmo pitch: " + str(pitch))
        if pitch is not None:
            mf.addNote(track=track,
                            channel=channel,
                            pitch=pitch,
                            time=note.offset,
                            duration=note.duration.quarterLength,
                            volume=VOLUME)

def add_note_to_midi(note, track, channel, mf):
    if note.isNote:
        # print("add note: " + str(note) + " pitch: " + str(note.pitch.ps) + " time: " + str(note.offset) +
        # " duration: " + str(note.duration.quarterLength))
        mf.addNote(track=track,
                        channel=channel,
                        pitch=int(note.pitch.ps),
                        time=note.offset,
                        duration=note.duration.quarterLength,
                        volume=VOLUME)

def convert_note_to_dexmo_note(note):
    if len(note.articulations) == 0:
        # print("no fingernumber")
        return None
    finger = note.articulations[0].fingerNumber
    # print("finger: " + str(finger))
    if finger == 1:
        # thumb
        return 29
    elif finger == 2:
        # idx
        return 41
    elif finger == 3:
        # mid
        return 53
    elif finger == 4:
        # ring
        return 65
    elif finger == 5:
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

    #midProc = MidiProcessing(left=True, right=True, bpm=120, outFiles=outFiles)

    generateMidi(noteValues=[1, 1 / 2, 1 / 4, 1 / 8],
                          notesPerBar=[2],  # range
                          noOfBars=noOfBars,
                          pitches=list(range(52, 68)),
                          bpm = 120,
                          left = False,
                          right = True,
                          outFiles=outFiles)
    #pitches=[48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72])

    # midProc.generate_metronome_and_fingers_for_midi('test_input/TripletsAndQuarters.mid', 8)
    #midProc.generate_metronome_and_fingers_for_midi(fileList=outFiles, noOfBars=noOfBars)
