#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum

class PracticeMode(enum.Enum):
    IDENTITY    = enum.auto()
    RIGHT_HAND = enum.auto()
    LEFT_HAND = enum.auto()
    SINGLE_NOTE = enum.auto()
    SLOWER      = enum.auto()
    
def apply_practice_mode(task_data, practice_mode):
    from task_generation.task import TaskData
    from task_generation.generator import TaskNote
    
    td = task_data
    if practice_mode == PracticeMode.IDENTITY:
        new_td = td.asdict()
        new_td["practice_mode"] = "None"
        return [TaskData(**new_td)], ["IDENTITY"]
    
    if practice_mode == PracticeMode.RIGHT_HAND:
        td_right = td.asdict()
        td_right["notes_left"] = []
        td_right["practice_mode"] = "right hand"
        td_right = TaskData(**td_right)
        return [td_right], ["SPLIT_HANDS_R"]

    if practice_mode == PracticeMode.LEFT_HAND:
        td_left = td.asdict()
        td_left["notes_right"] = []
        td_left["practice_mode"] = "split hands"
        td_left = TaskData(**td_left)
        return [td_left], ["SPLIT_HANDS_L"]
    
    if practice_mode == PracticeMode.SINGLE_NOTE:
        new_td = td.asdict()
        # transform all notes to one pitch (62/50)
        new_td["notes_right"] = [TaskNote(start, 62, duration) 
                                 for start, pitch, duration in new_td["notes_right"]]
        new_td["notes_left"] = [TaskNote(start, 50, duration) 
                                 for start, pitch, duration in new_td["notes_left"]]
        new_td["practice_mode"] = "single note"
        return [TaskData(**new_td)], ["SINGLE_NOTE"]
    
    if practice_mode == PracticeMode.SLOWER:
        new_td = td.asdict()
        new_td["bpm"] -= 20
        new_td["practice_mode"] = "slower"
        return [TaskData(**new_td)], ["SLOWER"]
    
    raise ValueError(f"Unexpected practice mode {practice_mode}!")
    
    
    
