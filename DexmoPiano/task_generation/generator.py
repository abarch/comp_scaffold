#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from dataclasses import dataclass, astuple, asdict
import dataclasses as dc
from task_generation.note_range_per_hand import NoteRangePerHand, get_pitchlist

from collections import namedtuple
from task_generation.task import TaskData

TaskNote = namedtuple("TaskNote", "start pitch duration")


INTRO_BARS = 1  # no. of empty first bars for metronome intro
ACROSS_BARS = False  # allow notes to reach across two bars

@dataclass
class TaskParameters:
    """
    @param bpm: Tempo (beats per minute).
    @param maxNoteperBar: Maximum number of notes that a bar can contain.
    @param numberOfBars: Total number of bars.
    @param noteValuesList: Possible durations of the notes (e.g. 1, 1/2 etc.).
    @param pitchesList: Possible MIDI pitch numbers (0-127).
    @param twoHandsTup: Tuple of booleans, True if left/right hand is active.
    """
    timeSignature: tuple    = (4,4)
    noteValues: list        = dc.field(default_factory= lambda: [1, 1 / 2, 1 / 4, 1 / 8] )
    maxNotesPerBar: int       = 3
    noOfBars: int           = 7
    note_range: NoteRangePerHand = NoteRangePerHand.C_TO_G
    left: bool              = False
    right: bool             = True
    bpm: float              = 120
    
    def astuple(self):
        return astuple(self)
    
        


def generate_task(task_parameters):
    return _generate_task_v1(task_parameters)

def _generate_task_v1(task_parameters): 
    ### EXERCISE GENERATION ###
    numerator, denominator = task_parameters.timeSignature

    # adjust no. of bars (in case of intro bars)
    bars = task_parameters.noOfBars + INTRO_BARS


    hands = list()
    if task_parameters.left:
        hands.append("left")
    if task_parameters.right:
        hands.append("right")
        
    data = dict(left=[], right=[])
    for hand in hands:
        pitches = get_pitchlist(task_parameters.note_range, right=hand=="right")
        ### CHOOSE TIME_AT_STARTSTEPS ###
    
        timesteps = []
        minNoteVal = min(task_parameters.noteValues)
    
        # randomly generate the chosen number of timesteps (notes) per bar
        stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
        for bar in range(task_parameters.noOfBars - 1):  # last bar is for extra notes
            # determine no. of notes in this bar
            noOfNotes = random.choice(range(1, task_parameters.maxNotesPerBar+1))
            noOfNotes = min(noOfNotes, len(stepRange))
    
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
            possNoteValues = [v for v in task_parameters.noteValues if v <= maxNoteVal]
            # if list is empty, increment time step by 1 and try again
            if not possNoteValues:
                print(t, timesteps[t], maxNoteVal)
                timesteps[t] = timesteps[t] + 1
                continue
    
            duration = random.choice(possNoteValues)
            pitch = random.choice(pitches)
    
            data[hand].append( TaskNote(timesteps[t], pitch, duration*denominator ) )
            
            if duration == 1/8:
                ## if the duration is 1/8, add a note right after to differentiate it more from 1/4
                pitch = random.choice(pitches)
                data[hand].append( TaskNote(timesteps[t]+0.5, pitch, duration*denominator ) )
    
            t += 1
    
    # data = sorted(data, key=lambda n: n.start)
    # return Task(time_sig=timeSig, noOfBars=bars, data=data)
    return TaskData(time_signature=task_parameters.timeSignature, number_of_bars=bars, 
                    bpm=float(task_parameters.bpm), note_range = task_parameters.note_range,
                notes_left=data["left"], notes_right=data["right"])