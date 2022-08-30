# [TaskNote(start=4, pitch=62, duration=2.0), TaskNote(start=8, pitch=60, duration=1.0), TaskNote(start=9, pitch=62,
# duration=1.0), TaskNote(start=10, pitch=60, duration=1.0), TaskNote(start=11, pitch=60, duration=1.0),
# TaskNote(start=12, pitch=60, duration=2.0), TaskNote(start=16, pitch=60, duration=1.0), TaskNote(start=17,
# pitch=62, duration=2.0), TaskNote(start=19, pitch=62, duration=1.0), TaskNote(start=20, pitch=62, duration=1.0),
# TaskNote(start=21, pitch=60, duration=1.0), TaskNote(start=22, pitch=62, duration=1.0), TaskNote(start=23,
# pitch=62, duration=1.0), TaskNote(start=24, pitch=62, duration=2.0)]
import math

import mido
from collections import namedtuple

from task_generation.task_data import TaskData
from task_generation.task_parameters import TaskParameters
from task_generation.note_range_per_hand import NoteRangePerHand

# from task_data import TaskData
# from task_parameters import TaskParameters
# from note_range_per_hand import NoteRangePerHand

TaskNote = namedtuple("TaskNote", "start pitch duration")

def midi2taskdata(midifile_path):
    midi = mido.MidiFile(midifile_path, clip=True)
    messages = []
    right, left = False, False
    if len(midi.tracks) == 2:
        right = True
        messages.append(midi.tracks[1])  # [1:-1]  # slice out meta information
    elif len(midi.tracks) > 2:
        right, left = True, True
        messages.append(midi.tracks[1])
        messages.append(midi.tracks[2])
    bpm, time_signature, n_beats = -1, -1, -1

    for msg in midi.tracks[0]:
        if msg.type == 'set_tempo':
            bpm = mido.tempo2bpm(msg.tempo)
        if msg.type == 'time_signature':
            time_signature = (msg.numerator, msg.denominator)
        if msg.type == 'end_of_track':
            n_beats = msg.time / midi.ticks_per_beat

    noOfBars = math.ceil(n_beats / time_signature[0]) + 2

    notes = dict(left=[], right=[])

    for track in messages:
        passed_time = time_signature[0]
        for i in range(len(track) - 1):
            if track[i].type != 'note_on' and track[i].type != 'note_off':
                continue
            passed_time += track[i].time / midi.ticks_per_beat
            if track[i].velocity != 0 and track[i].type == 'note_on':
                if track[i].channel == 0:
                    notes["right"].append(
                        TaskNote(passed_time, track[i].note, float(track[i + 1].time) / midi.ticks_per_beat))
                elif track[i].channel == 1:
                    notes["left"].append(
                        TaskNote(passed_time, track[i].note, float(track[i + 1].time) / midi.ticks_per_beat))

    task_parameter = TaskParameters(
        timeSignature=time_signature,
        maxNotesPerBar=16,
        noOfBars=noOfBars,
        note_range_right=NoteRangePerHand.ONE_OCTAVE,  # where does this come from?
        note_range_left=NoteRangePerHand.ONE_OCTAVE,
        right=right,
        left=left,
        alternating=False,
        bpm=bpm
    )

    task_data = TaskData(
        parameters=task_parameter,
        time_signature=time_signature,
        number_of_bars=noOfBars,
        notes_left=notes["left"],
        notes_right=notes["right"],
        bpm=bpm
    )

    return task_data


if __name__ == '__main__':
    pass
