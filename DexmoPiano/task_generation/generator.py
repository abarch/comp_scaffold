#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import random
from dataclasses import dataclass, astuple, asdict
import dataclasses as dc

import numpy as np
from task_generation.note_range_per_hand import NoteRangePerHand, get_pitchlist, transpose

from collections import namedtuple
from task_generation.task import TaskData

TaskNote = namedtuple("TaskNote", "start pitch duration")


INTRO_BARS = 1  # no. of empty first bars for metronome intro
ACROSS_BARS = False  # allow notes to reach across two bars

@dataclass
class TaskParameters:
    """
    @param bpm: Tempo (beats per minute).
    @param maxNotesPerBar: Maximum number of notes that a bar can contain.
    @param numberOfBars: Total number of bars.
    @param noteValuesList: Possible durations of the notes (e.g. 1, 1/2 etc.).
    @param pitchesList: Possible MIDI pitch numbers (0-127).
    @param alternating: if true play left/right alternating instead of simultaneously
    @param twoHandsTup: Tuple of booleans, True if left/right hand is active.
    """
    timeSignature: tuple    = (4,4)
    noteValues: list        = dc.field(default_factory= lambda: [1 / 2, 1 / 4] )
    maxNotesPerBar: int       = 3
    noOfBars: int           = 7
    note_range_right: NoteRangePerHand = NoteRangePerHand.TWO_NOTES
    #FIXME: debug
    note_range_left: NoteRangePerHand = NoteRangePerHand.ONE_NOTE
    left: bool              = False
    right: bool             = True
    alternating: bool     = True
    bpm: float              = 100
    
    def astuple(self):
        return astuple(self)
    
def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


def generate_task(task_parameters):
    return _generate_task_v1(task_parameters)

def _generate_task_v1(task_parameters): 
    ### EXERCISE GENERATION ###
    numerator, denominator = task_parameters.timeSignature

    # adjust no. of bars (in case of intro bars)
    bars = task_parameters.noOfBars + INTRO_BARS


        
    data = dict(left=[], right=[])

    def getpitches(note_range, base):
        nl = get_pitchlist(note_range)
        tnl = transpose(nl, base)
        return tnl

    def get_timesteps(hand, note_range,base):
        pitches = getpitches (note_range, base)
        print("pitchlist", pitches)
        ### CHOOSE TIME_AT_STARTSTEPS ###

        timesteps = []
        minNoteVal = min(task_parameters.noteValues)

        # randomly generate the chosen number of timesteps (notes) per bar
        stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
        print("stepRange", stepRange)
        for bar in range(task_parameters.noOfBars - 1):  # last bar is for extra notes
            # determine no. of notes in this bar
            noOfNotes = random.choice(range(1, task_parameters.maxNotesPerBar+4)) #add a lot to maxNotesPerBar to get less pauses
            noOfNotes = min(noOfNotes, len(stepRange))

            # shift step numbers
            shift = (bar + INTRO_BARS) * numerator
            steps = [temp + shift for temp in stepRange]
            print("steps", steps)

            new_steps = [steps[0]] #add note at beginning of every bar so there are less pauses
            new_steps.append(random.sample(steps[1:], noOfNotes-1))
            flat_steps = [a for i in new_steps for a in flatten(i)]
            timesteps.append(flat_steps)

        # flatten and sort list
        timesteps = sorted([item for sublist in timesteps for item in sublist])

        # append dummy element to avoid additional bar
        timesteps.append(bars * numerator)

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

            # introduce some randomness, so large values are more equally likely getting picked
            if random.random() > 0.4:
                duration = random.choice(possNoteValues)
            else:
                duration = max(possNoteValues)
            pitch = random.choice(pitches)

            data[hand].append(TaskNote(timesteps[t], pitch, duration * denominator))

            if duration == 1 / 8:
                ## if the duration is 1/8, add a note right after to differentiate it more from 1/4
                pitch = random.choice(pitches)
                data[hand].append(TaskNote(timesteps[t] + 0.5, pitch, duration * denominator))

            t += 1

    #for hand in hands:
    if task_parameters.left:
        get_timesteps("left", note_range_left, base_note = 48) #C3)
    if task_parameters.right:
        get_timesteps("right", note_range_right)
        # print("note range name", task_parameters.note_range_)
        # pitches = get_pitchlist(task_parameters.note_range, right=hand=="right")
        #print("pitchlist", pitches)
        ### CHOOSE TIME_AT_STARTSTEPS ###
    
        # timesteps = []
        # minNoteVal = min(task_parameters.noteValues)
        #
        # # randomly generate the chosen number of timesteps (notes) per bar
        # stepRange = [temp for temp in range(numerator) if temp % (minNoteVal * numerator) == 0]
        # print("stepRange", stepRange)
        # for bar in range(task_parameters.noOfBars - 1):  # last bar is for extra notes
        #     # determine no. of notes in this bar
        #     noOfNotes = random.choice(range(1, task_parameters.maxNotesPerBar+4)) #add a lot to maxNotesPerBar to get less pauses
        #     noOfNotes = min(noOfNotes, len(stepRange))
        #
        #     # shift step numbers
        #     shift = (bar + INTRO_BARS) * numerator
        #     steps = [temp + shift for temp in stepRange]
        #     print("steps", steps)
        #
        #     new_steps = [steps[0]] #add note at beginning of every bar so there are less pauses
        #     new_steps.append(random.sample(steps[1:], noOfNotes-1))
        #     flat_steps = [a for i in new_steps for a in flatten(i)]
        #     timesteps.append(flat_steps)
        #
        # # flatten and sort list
        # timesteps = sorted([item for sublist in timesteps for item in sublist])
        #
        # # append dummy element to avoid additional bar
        # timesteps.append(bars * numerator)
        #
        # # print("timesteps:", timesteps[:-1])
        #
        ### ADD PIANO NOTES ###
        # add music (piano) notes

        # custom for-loop
        # t = 0
        # while t < (len(timesteps) - 1):
        #     # compute maximum note length until next note
        #     maxNoteVal = (timesteps[t + 1] - timesteps[t]) / denominator
        #     ###temp = maxNoteVal
        #
        #     # compute maximum note length until next bar
        #     if not ACROSS_BARS:
        #         maxToNextBar = 1 - ((timesteps[t] % denominator) / denominator)
        #         maxNoteVal = min([maxNoteVal, maxToNextBar])
        #
        #     ###print(timesteps[t], "min(", temp, maxToNextBar, ") =", maxNoteVal)
        #
        #     # calculate possible note values at current time step
        #     possNoteValues = [v for v in task_parameters.noteValues if v <= maxNoteVal]
        #     # if list is empty, increment time step by 1 and try again
        #     if not possNoteValues:
        #         print(t, timesteps[t], maxNoteVal)
        #         timesteps[t] = timesteps[t] + 1
        #         continue
        #
        #     # introduce some randomness, so large values are more equally likely getting picked
        #     if random.random() > 0.4:
        #         duration = random.choice(possNoteValues)
        #     else:
        #         duration = max(possNoteValues)
        #     pitch = random.choice(pitches)
        #
        #     data[hand].append(TaskNote(timesteps[t], pitch, duration * denominator))
        #
        #     if duration == 1 / 8:
        #         ## if the duration is 1/8, add a note right after to differentiate it more from 1/4
        #         pitch = random.choice(pitches)
        #         data[hand].append(TaskNote(timesteps[t] + 0.5, pitch, duration * denominator))
        #
        #     t += 1
        #

    hands = list()
    if task_parameters.left:
        hands.append("left")
    if task_parameters.right:
        hands.append("right")

    # play with both hands alternating, instead of together at the same time
    if task_parameters.alternating:
        if task_parameters.left and task_parameters.right: #only if task with both hands as well
            for hand in ["left", "right"]:
                if hand == "left":
                    note_starts = [8,9,10,11,16,17,18,19,24,25,26,27]
                else:
                    note_starts = [4,5,6,7,12,13,14,15,20,21,22,23]
                remove = []
                for task in data[hand]:
                    if task.start not in note_starts:
                        remove.append(task)
                for item in remove:
                    data[hand].remove(item)

    # data = sorted(data, key=lambda n: n.start)
    # return Task(time_sig=timeSig, noOfBars=bars, data=data)
    return TaskData(time_signature=task_parameters.timeSignature, number_of_bars=bars, 
                    bpm=float(task_parameters.bpm), note_range = task_parameters.note_range,
                notes_left=data["left"], notes_right=data["right"])