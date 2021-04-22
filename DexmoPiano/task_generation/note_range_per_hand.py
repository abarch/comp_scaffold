#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum

class NoteRangePerHand(enum.Enum):
    UNKOWN = enum.auto()
    
    ONE_NOTE = enum.auto()
    TWO_NOTES = enum.auto()
    C_TO_G = enum.auto()
    ONE_OCTAVE = enum.auto()
    ONE_OCTAVE_WHITE = enum.auto()
    ONE_OCTAVE_BLACK = enum.auto()
    
    
noteRangePerHandDescription = ["One note (C)", "Two notes (C,D)", 
                               "Notes C-G (for 5 fingers)", "One octave",
                               "One octave (only white keys)",
                               "One octave (only black keys)"
                               ]

noteRangeMap = {const: desc for const, desc in 
                zip(list(NoteRangePerHand)[1:], noteRangePerHandDescription)}
noteRangeMap.update(                   
                    {desc: const for const, desc in 
                zip(list(NoteRangePerHand)[1:], noteRangePerHandDescription)}
                    )

def get_pitchlist(note_range, right=True):
    if right:
        base_note = 60 #C4
    else:
        base_note = 48 #C3
        
    if note_range == NoteRangePerHand.ONE_NOTE:
        pitchesList = [0]
    elif note_range == NoteRangePerHand.TWO_NOTES:
        pitchesList = [0, 2]
    elif note_range == NoteRangePerHand.C_TO_G:
        pitchesList = [0, 2, 4, 5, 7]
    elif note_range == NoteRangePerHand.ONE_OCTAVE:
        pitchesList = list(range(0, 12))
    elif note_range == NoteRangePerHand.ONE_OCTAVE_WHITE:
        pitchesList = [0,2,4,5,7,9,11]
    elif note_range == NoteRangePerHand.ONE_OCTAVE_BLACK:
        pitchesList = [1,3,6,8,10]
    else:
        raise ValueError(f"got unexpected note_range {repr(note_range)}!")
        
    return [base_note + p for p in pitchesList]
    