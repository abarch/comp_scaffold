#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from dataclasses import dataclass, asdict, astuple
from task_generation.practice_modes import apply_practice_mode
from task_generation.note_range_per_hand import NoteRangePerHand


@dataclass(frozen=True)
class TaskData:
    time_signature: tuple
    number_of_bars: int
    note_range:  NoteRangePerHand
    notes_right: list
    notes_left:  list
    bpm: float
    _all_notes_fixed: tuple = None
    
    def asdict(self):
        return asdict(self)
    
    def astuple(self):
        return astuple(self)
    
    def beats_per_measure(self):
        return self.time_signature[0]
    
    # def generate_practice_mode(self, practice_mode):
    #     pass

    def note2hand(self, note):
        if note in self.notes_right:
            return "right"
        if note in self.notes_left:
            return "left"
        raise ValueError()
        
    def all_notes(self):
        if self._all_notes_fixed:
            return self._all_notes_fixed
        self._all_notes_fixed = tuple(sorted(self.notes_left + self.notes_right, key=lambda n:n.start))
        return self._all_notes_fixed
    
    def __repr__(self):
        h = str(id(self))[-5:]
        return f"<TaskData obj {h}>"
    
    def __hash__(self):
        d = self.asdict()
        d["notes_right"] = tuple(d["notes_right"])
        d["notes_left"] = tuple(d["notes_left"])
        return hash(tuple(d.items()))
    
"""
What is a task? 

in regards to how the score is generated:
    - task parameters (might be sidestepped by loading midi)

in regards to playing it:
    - midi file (with metronome etc)
    - musicxml file (finger numbers)

after it was played:
    - errors

"""
    
class TargetTask():
    def from_midi(midi_file):
        return NotImplementedError()
        # return TargetTask(from_midi=True)
    
    def from_task_parameters(task_parameters):
        from task_generation.generator import generate_task
        task_data = generate_task(task_parameters)
        return TargetTask(task_data, task_parameters=task_parameters)
    
    def __init__(self, task_data, task_parameters=None, from_midi=False):
        self.task_data = task_data
        self.task_parameters = task_parameters
        self.from_midi = from_midi
        self.subtask_queue = [("TARGET", self.task_data)]
        self.subtask_queue_index = 0
        
        self.errordict = defaultdict(list)
        
    def queue_practice_mode(self, practice_mode):
        new_task_data, description = apply_practice_mode(self.task_data, practice_mode)
        self.subtask_queue_index = len(self.subtask_queue)
        self.subtask_queue.extend(zip(description, new_task_data))
        
    def single_target_eval_at_end(self):
        self.subtask_queue_index = 0
        target_eval = ("TARGET", self.task_data)
        while target_eval in self.subtask_queue:
            self.subtask_queue.remove(target_eval)
        self.subtask_queue.append(target_eval)
        
    def current_task_data(self):
        print("(TARGET TASK) subtask queue:", self.subtask_queue, "[", self.subtask_queue_index, "]")
        return self.subtask_queue[self.subtask_queue_index][1] #its a name, data tuple
    
    def register_error(self, error, task_data=None):
        task_data = task_data or self.current_task_data()
        self.errordict[task_data].append(error)
    
    def next_subtask_exists(self):
        return self.subtask_queue_index < len(self.subtask_queue) -1 
    
    def next_subtask(self):
        if not self.next_subtask_exists():
            raise IndexError()
            
        self.subtask_queue_index += 1
        return self.current_task_data()
    
    def previous_subtask_exists(self):
        return self.subtask_queue_index > 0
    
    def previous_subtask(self):
        if not self.previous_subtask_exists():
            raise IndexError()
            
        self.subtask_queue_index -= 1
        return self.current_task_data()
        
    