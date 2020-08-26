from midiutil.MidiFile import MIDIFile

import copy
import os
import random

import pianoplayer_interface


def convert_note_to_dexmo_note(note):
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


def add_dexmo_note_to_midi(note, track, channel, volume, mf):
    if note.isNote:
        # print("note: " + str(note) + " pitch: " + str(note.pitch.ps))
        pitch = convert_note_to_dexmo_note(note)
        # print("dexmo pitch: " + str(pitch))
        if pitch is not None:
            mf.addNote(track=track,
                       channel=channel,
                       pitch=pitch,
                       time=int(note.offset),
                       duration=note.duration.quarterLength,
                       volume=volume)


# some code taken from https://github.com/Michael-F-Ellis/tbon

def generateMidi(bpm, noteValues, notesPerBar, noOfBars, pitches, twoHands, outFiles):
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

    NUM_OF_TRACKS = 2 + twoHands

    ### INITIALIZATION ###

    # create MIDI object
    mf = MIDIFile(numTracks=5)  # right (+ left) hand + metronome

    # TODO: make constant?
    rTrack = 0  # right hand track
    lTrack = 1  # left hand track
    mTrack = 2  # metronome track
    rdTrack = 3  # right hand dexmo track
    ldTrack = 4  # left hand dexmo track

    # if twoHands:
    mf.addTrackName(lTrack, TIME, "Left Hand")
    mf.addTrackName(rTrack, TIME, "Right Hand")
    mf.addTrackName(mTrack, TIME, "Metronome")
    mf.addTrackName(ldTrack, TIME, "Left Hand Dexmo")
    mf.addTrackName(rdTrack, TIME, "Right Hand Dexmo")

    mf.addTempo(rTrack, TIME, bpm)  # in file format 1, track doesn't matter

    ### EXERCISE GENERATION ###

    # time signature (ex. 4/4 = (4, 4))
    # TODO: USE AS INPUT?
    timeSig = (4, 4)

    numerator = timeSig[0]
    denominator = timeSig[1]
    # map denominator to power of 2 for MIDI
    midiDenom = {2: 1, 4: 2, 8: 3, 16: 4}[denominator]

    # adjust no. of bars (in case of intro bars)
    bars = noOfBars + INTRO_BARS

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

    mf.addTimeSignature(track=rTrack,
                        time=TIME,
                        numerator=numerator,
                        denominator=midiDenom,
                        clocks_per_tick=metro_clocks)

    ### CHOOSE TIMESTEPS ###

    timesteps = []
    minNoteVal = min(noteValues)

    # randomly generate the chosen number of timesteps (notes) per bar
    stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
    for bar in range(noOfBars):
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
    mf.addProgramChange(rTrack, CHANNEL_PIANO, TIME, INSTRUM_PIANO)
    mf.addProgramChange(lTrack, CHANNEL_PIANO, TIME, INSTRUM_PIANO)

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
        if twoHands and (pitch < 60):
            handTrack = lTrack
        else:
            handTrack = rTrack

        # print("original note pitches: " + str(pitch))
        mf.addNote(track=handTrack,
                   channel=CHANNEL_PIANO,
                   pitch=pitch,
                   time=timesteps[t],
                   duration=denominator * duration,
                   volume=VOLUME)

        t += 1

    # write 1st MIDI file (piano only)
    with open(outFiles[0], 'wb') as outf:
        # copy object, avoid reference
        copy.deepcopy(mf).writeFile(outf)

    ### METRONOME ###

    # add metronome notes
    mf.addProgramChange(mTrack, CHANNEL_METRO, TIME, INSTRUM_DRUMS)

    for t in range(bars * numerator):

        # decide if downbeat or 'other' note
        if (t % numerator) == 0:
            # first beat in bar
            pitch = PITCH_METRO_HI
        else:
            pitch = PITCH_METRO_LO

        mf.addNote(track=mTrack,
                   channel=CHANNEL_METRO,
                   pitch=pitch,
                   time=t,
                   duration=1,
                   volume=VOLUME)

    # write 2nd MIDI file (with metronome)
    with open(outFiles[1], 'wb') as outf:
        # mf.writeFile(outf)
        copy.deepcopy(mf).writeFile(outf)

    ### add fingernumbers ###
    mf.addProgramChange(rdTrack, CHANNEL_RH, TIME, INSTRUM_DEXMO)
    mf.addProgramChange(ldTrack, CHANNEL_LH, TIME, INSTRUM_DEXMO)

    pianoplayer = pianoplayer_interface.PianoplayerInterface(outFiles[0])
    pianoplayer.generate_fingernumbers(False, not twoHands, 0, 1, noOfBars)
    # pianoplayer.generate_fingernumbers(False, False, 0, 1, noOfBars)
    pianoplayer.write_output("output/output.xml")
    sf = pianoplayer.get_score()
    for note in sf.parts[0].notesAndRests:
        add_dexmo_note_to_midi(note, rdTrack, CHANNEL_RH, VOLUME, mf)
    if twoHands:
        for note in sf.parts[1].notesAndRests:
            add_dexmo_note_to_midi(note, ldTrack, CHANNEL_LH, VOLUME, mf)

    # write 3rd MIDI file (with dexmo notes)
    with open(outFiles[2], 'wb') as outf:
        copy.deepcopy(mf).writeFile(outf)
        # mf.writeFile(outf)


if __name__ == "__main__":

    # create folder if it does not exist yet
    outDir = "./output/"
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    generateMidi(bpm=120,
                 noteValues=[1, 1 / 2, 1 / 4, 1 / 8],
                 notesPerBar=[1],  # range
                 noOfBars=40,
                 pitches=[48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72],
                 # pitches=[60, 62, 64, 65, 67, 69, 71, 72], # right hand only
                 # pitches=list(range(52, 68)),
                 twoHands=True,
                 outFiles=["./output/output.mid", "./output/output-m.mid", "./output/output-md.mid"])
