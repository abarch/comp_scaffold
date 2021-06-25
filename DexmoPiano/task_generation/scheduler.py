#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import functools
from task_generation.generator import generate_task
from task_generation.task import TargetTask

class Scheduler:
    def __init__(self, load_next_task_func):
        ## load the heuristics
        
        self.task_queue = list()
        self.task_queue_index = 0
        
        #if there are tasks in here they have to be executed
        self.task_movement = list()
        self.task_movement_errors = list()
        self.task_movement_eval_func = functools.partial(print, "TASK_MOVEMENT_ERRORS:")
        
        self.load_next_task_func = load_next_task_func
    
    def in_task_movement(self):
        return len(self.task_movement) > 0
    
    def new_task_forced_practice_sequence_prior(self, task_parameters_fallback, 
                                                list_of_practice_modes):
        self.get_new_target_task(task_parameters_fallback)
        tt = self.current_target_task
        
        for pm in list_of_practice_modes:
            tt.queue_practice_mode(pm)
        tt.single_target_eval_at_end()
        self.task_movement = copy.deepcopy(tt.subtask_queue)
        self.task_movement_errors = list()
        
    
    def get_new_target_task(self, task_parameters_fallback):
        best_task_params = self.get_optimal_task_parameters(fallback=task_parameters_fallback)
        self.current_target_task = TargetTask.from_task_parameters(best_task_params)

        
        self.task_queue.append(self.current_target_task)
        self.task_queue_index = len(self.task_queue) -1
        return self.current_task_data()
    
    def _current_target_task(self):
        return self.task_queue[self.task_queue_index]
    
    def current_task_data(self):
        if self.in_task_movement():
            print("(SCHEDULER) IN TASK MOVEMENT")
            return self.task_movement[0][1]
        
        print("(SCHEDULER) task queue:", self.task_queue, "[", self.task_queue_index, "]")
        return self._current_target_task().current_task_data()
    
    def get_next_task(self, taskParameters):
        # if self.in_task_movement():
        #     self.task_movement.pop(0)
        #     if len(self.task_movement) > 0:
        #         return self.task_movement[0]
        #     else:
                
            
        if len(self.task_queue) == 0:
            return self.get_new_target_task(taskParameters)
        
        if self._current_target_task().next_subtask_exists():
            return self._current_target_task().next_subtask()
        
        
        if self.next_task_exists():
            self.task_queue_index += 1
            return self.current_task_data()
        
        return self.get_new_target_task(taskParameters)
        # return generate_task(taskParameters)
    
    def get_previous_task(self):
        # try to go to the prev subtask of the current target task
        if self._current_target_task().previous_subtask_exists():
            return self._current_target_task().previous_subtask()
        
        
        if self.previous_task_exists():
            self.task_queue_index -= 1
            return self.current_task_data()
        
        raise ValueError("There is no previous task!")
    
    def queue_practice_mode(self, practice_mode):
        self._current_target_task().queue_practice_mode(practice_mode)
    
    def get_optimal_task_parameters(self, fallback):
        return fallback
    
    def info(self):
        pass
    
    def previous_task_exists(self):
        if self.in_task_movement():
            return False
        
        return self._current_target_task().previous_subtask_exists() or \
            self.task_queue_index > 0
    
    def next_task_exists(self):
        if self.in_task_movement():
            # we want to control everything while in task movement
            return False 
        
        return self._current_target_task().next_subtask_exists() or \
            self.task_queue_index < len(self.task_queue)-1
            
    def register_error(self, error):
        if self.in_task_movement():
            task_data = self.task_movement.pop(0)
            self.task_movement_errors.append(error)
            self._current_target_task().register_error(error, task_data)
            
            if len(self.task_movement) == 0:
                # empty after pop
                self.task_movement_eval_func(*self.task_movement_errors)
                
            else:
                self.load_next_task_func()
        
        else:
            self._current_target_task().register_error(error)
    
# def getTimeSortedMidiFiles():
#     """
#     Finds all files with .mid suffix in a directory and sorts them by their timestamp.

#     @return: Sorted list of MIDI files.
#     """
#     import os
#     ll = os.listdir(outputDir)
#     files = [x.split('.')[0] for x in ll if '.mid' in x]
    
#     files.sort()
#     return files

    
def choosePracticeMode(tk_root):
    import tkinter as tk
    global_var_name = "_NEXT_TASK_GEN_OPTION"
    
    new_window = tk.Toplevel(tk_root)
    
    import functools
    def set_option(option):
        def set_option_actual(option):
            
            globals()[global_var_name] = option
            new_window.destroy()
            
        return functools.partial(set_option_actual, option)
    
    
    
    
    b = tk.Button(new_window, text="NEW TASK", command=set_option("NEW_TASK"))
    b.pack(side = tk.TOP, padx=5, pady=15)
    
    b = tk.Button(new_window, text="TEST MOVEMENT 1", command=set_option("TEST_MOVEMENT_1"))
    b.pack(side = tk.TOP, padx=5, pady=15)

    b = tk.Button(new_window, text="Next Complexity Level", command=set_option("NEXT_LEVEL"))
    b.pack(side=tk.TOP, padx=5, pady=15)
    
    l = tk.Label(new_window, text="Same task, but training mode:")
    l.pack(side = tk.TOP, padx=5, pady=1)
    
    from task_generation.practice_modes import PracticeMode
    for pm in PracticeMode:
        b = tk.Button(new_window, text=pm.name, command=set_option(pm),
                      padx=5, pady=5)
        b.pack(side = tk.TOP)
        b.bind
        
    
    tk_root.wait_window(new_window)
    
    val = globals()[global_var_name]
    del globals()[global_var_name]
    return val


def threshold_info(tk_root):
    import tkinter as tk

    new_window = tk.Toplevel(tk_root)

    l = tk.Label(new_window, text="I think this needs some more practise. How about we try out different practise "
                                  "modes and learn together.")
    l.pack(side=tk.TOP, padx=5, pady=1)

    def close():
        new_window.destroy()

    b = tk.Button(new_window, text="Okay", command=close)
    b.pack(side=tk.TOP, padx=5, pady=15)


