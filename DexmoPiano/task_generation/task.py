#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses as dc
from collections import defaultdict
from dataclasses import dataclass, asdict, astuple

from task_generation.note_range_per_hand import NoteRangePerHand
from task_generation.practice_modes import PracticeMode


@dataclass
class MidiNoteEventContainer:
    left: list = dc.field(init=False)
    right: list = dc.field(init=False)
    together: list = dc.field(init=False)

    def register_midi_events(self, midi_left, midi_right):
        self.left = midi_left
        self.right = midi_right
        self.together = sorted(self.left + self.right, key=lambda n: n.note_on_time)

    def __repr__(self):
        try:
            return super().__repr__()
        except:
            return "MidiNoteEventContainer"



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
    timeSignature: tuple = (4, 4)
    noteValues: list = dc.field(default_factory=lambda: [1 / 2, 1 / 4])
    maxNotesPerBar: int = 3
    noOfBars: int = 7
    note_range_right: NoteRangePerHand = NoteRangePerHand.TWO_NOTES
    # FIXME: debug
    note_range_left: NoteRangePerHand = NoteRangePerHand.ONE_NOTE
    left: bool = False
    right: bool = True
    alternating: bool = True
    bpm: float = 100

    def astuple(self):
        return astuple(self)


@dataclass(frozen=False)  # Maor: it was changed to False so the bpm could be changed.
class TaskData:
    parameters: TaskParameters
    time_signature: tuple
    number_of_bars: int
    notes_right: list
    notes_left: list
    bpm: float
    midi: MidiNoteEventContainer = dc.field(default_factory=MidiNoteEventContainer)
    practice_mode: str = "None"

    def __post_init__(self):
        assert type(self.midi) != dict

    def asdict(self):
        _d = asdict(self)
        _d["midi"] = self.midi  # the midi container gets turned into a dict!?
        _d["parameters"] = self.parameters
        return _d

    def astuple(self):
        return astuple(self)

    def beats_per_measure(self):
        return self.time_signature[0]

    def note2hand(self, note):
        if note in self.midi.right:
            return "right"
        if note in self.midi.left:
            return "left"
        raise ValueError("note in neither lists?")

    def all_notes(self):
        assert hasattr(self.midi, "together"), "MidiContainer didn't have any events yet?"
        return self.midi.together

    def __repr__(self):
        h = str(id(self))[-5:]
        return f"<TaskData obj {h}>"

    def __hash__(self):
        d = self.asdict()
        d["notes_right"] = tuple(d["notes_right"])
        d["notes_left"] = tuple(d["notes_left"])

        # the midi data is kind of not related to the task itself, thus
        # shouldn't result in a different hash if different.
        del d["midi"]
        del d["parameters"]
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


class TargetTask:

    def __init__(self, task_data: TaskData):
        self.task_data = task_data

        # FIXME :  add comment what is subtask_queue
        self.subtask_queue = [("TARGET", self.task_data)]  # type: list[(str, TaskData)]
        self.subtask_queue_index = 0

        self.error_dict = defaultdict(list)  # map subtask to list of error

    @staticmethod
    def from_task_parameters(task_parameters: TaskParameters):
        task_data = generate_task(task_parameters)
        return TargetTask(task_data)

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

    def current_task_data(self) -> TaskData:
        print("(TARGET TASK) subtask queue:", self.subtask_queue, "[", self.subtask_queue_index,
              "]")
        return self.subtask_queue[self.subtask_queue_index][1]  # its a name, data tuple

    def register_error(self, error, task_data=None):
        task_data = task_data or self.current_task_data()
        self.error_dict[task_data].append(error)

    def next_subtask_exists(self) -> bool:
        return self.subtask_queue_index < len(self.subtask_queue) - 1

    def next_subtask(self) -> TaskData:
        if not self.next_subtask_exists():
            raise IndexError()

        self.subtask_queue_index += 1
        return self.current_task_data()

    def previous_subtask_exists(self) -> bool:
        return self.subtask_queue_index > 0

    def previous_subtask(self) -> TaskData:
        if not self.previous_subtask_exists():
            raise IndexError()

        self.subtask_queue_index -= 1
        return self.current_task_data()



def apply_practice_mode(task_data, practice_mode) -> tuple[list[object], list[str]]:
    from task_generation.task import TaskData
    from task_generation.generator import TaskNote

    if practice_mode == PracticeMode.IDENTITY:
        new_td = task_data.asdict()
        new_td["practice_mode"] = "None"
        return [TaskData(**new_td)], ["IDENTITY"]

    if practice_mode == PracticeMode.RIGHT_HAND:
        td_right = task_data.asdict()
        td_right["notes_left"] = []
        td_right["practice_mode"] = "right hand"
        td_right = TaskData(**td_right)
        return [td_right], ["SPLIT_HANDS_R"]

    if practice_mode == PracticeMode.LEFT_HAND:
        td_left = task_data.asdict()
        td_left["notes_right"] = []
        td_left["practice_mode"] = "split hands"
        td_left = TaskData(**td_left)
        return [td_left], ["SPLIT_HANDS_L"]

    if practice_mode == PracticeMode.SINGLE_NOTE:
        new_td = task_data.asdict()
        # transform all notes to one pitch (62/50)
        new_td["notes_right"] = [TaskNote(start, 62, duration)
                                 for start, pitch, duration in new_td["notes_right"]]
        new_td["notes_left"] = [TaskNote(start, 50, duration)
                                for start, pitch, duration in new_td["notes_left"]]
        new_td["practice_mode"] = "single note"
        return [TaskData(**new_td)], ["SINGLE_NOTE"]

    if practice_mode == PracticeMode.SLOWER:
        new_td = task_data.asdict()
        new_td["bpm"] -= 20
        new_td["practice_mode"] = "slower"
        return [TaskData(**new_td)], ["SLOWER"]

    raise ValueError(f"Unexpected practice mode {practice_mode}!")