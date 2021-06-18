#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum

class NoteRangePerHand(enum.Enum):
    UNKOWN = enum.auto()
    
    ONE_NOTE = enum.auto()
    TWO_NOTES = enum.auto()
    C_TO_G = enum.auto()
    ONE_OCTAVE = enum.auto()
    C_DUR= enum.auto()
    A_MOLL = enum.auto()
    ONE_OCTAVE_BLACK = enum.auto()
    
    
noteRangePerHandDescription = ["One note (C)", "Two notes (C,D)", 
                               "Notes C-G (for 5 fingers)", "One octave",
                               "C-Dur", "A-Moll",
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

    # Typecast to string, bc weird error gives false comparison otherwise
    if str(note_range) == str(NoteRangePerHand.ONE_NOTE):
        pitchesList = [0]
    elif str(note_range) == str(NoteRangePerHand.TWO_NOTES):
        pitchesList = [0, 2]
    elif str(note_range) == str(NoteRangePerHand.C_TO_G):
        pitchesList = [0, 2, 4, 5, 7]
    elif str(note_range) == str(NoteRangePerHand.ONE_OCTAVE):
        pitchesList = list(range(0, 12))
    elif str(note_range) == str(NoteRangePerHand.C_DUR):
        pitchesList = [0,2,4,5,7,9,11]
    elif str(note_range) == str(NoteRangePerHand.A_MOLL):
        pitchesList = [-3, -1, 0, 2, 4, 5, 8]
    elif str(note_range) == str(NoteRangePerHand.ONE_OCTAVE_BLACK):
        pitchesList = [1,3,6,8,10]
    else:
        raise ValueError(f"got unexpected note_range {repr(note_range)}!")
        
    return [base_note + p for p in pitchesList]
    