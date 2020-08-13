from midiutil.MidiFile import MIDIFile

import copy
import os
import random


# some code taken from https://github.com/Michael-F-Ellis/tbon

def generateMidi(bpm, noteValues, notesPerBar, noOfBars, pitches, twoHands, outFiles):

    ### CONSTANTS ###

    CHANNEL_PIANO = 0
    CHANNEL_METRO = 9

    INSTRUM_PIANO = 0
    INSTRUM_DRUMS = 9

    PITCH_METRO_HI = 76  # high wood block
    PITCH_METRO_LO = 77  # low wood block

    VOLUME = 100

    TIME = 0  # start at the beginning

    INTRO_BARS = 1  # no. of empty first bars for metronome intro

    ACROSS_BARS = 0  # allow notes to reach across two bars

    NUM_OF_TRACKS = 2 + twoHands


    ### INITIALIZATION ###

    # create MIDI object
    mf = MIDIFile(numTracks=3)  # right (+ left) hand + metronome

    # TODO: make constant?
    rTrack = 0  	# right hand track
    lTrack = 1		# left hand track
    mTrack = 2      # metronome track
    

    #if twoHands:
    mf.addTrackName(lTrack, TIME, "Left Hand")
    mf.addTrackName(rTrack, TIME, "Right Hand")
    mf.addTrackName(mTrack, TIME, "Metronome")

    mf.addTempo(rTrack, TIME, bpm)	# in file format 1, track doesn't matter


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
        mf.writeFile(outf)


if __name__ == "__main__":

    # create folder if it does not exist yet
    outDir = "./output/"
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    generateMidi(bpm=120,
                 noteValues=[1, 1/2, 1/4, 1/8],
                 notesPerBar=[1],  # range
                 noOfBars=8,
                 #pitches=[60, 62, 64, 65, 67, 69, 71, 72],
                 pitches=list(range(52, 68)),
                 twoHands=True,
                 outFiles=["./output/output.mid", "./output/output-m.mid"])
