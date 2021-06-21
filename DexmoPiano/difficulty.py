from DexmoPiano.task_generation.generator import TaskParameters
from DexmoPiano.task_generation.note_range_per_hand import NoteRangePerHand


def getTaskComplexity(previous=None):
    levels = []

    ranges = list(NoteRangePerHand)[2:]
    value = [1/2, 1/4]
    hands = ["right", "left"]
    right = False
    left = False

    for i in range(len(ranges)):
        if i == 1:
            hands.append("both")
        if i == 2:
            value.append(1)
        if i == 3:
            value.append(1/8)
        if i == 4:
            value.append(1/16)
        for h in hands:
            if h == "right":
                right = True
                left = False
            elif h == "left":
                left = True
                right = False
            else:
                right = left = True
            par = TaskParameters((4,4), value.copy(), 3, 7, ranges[i], left, right, 100)
            # timeSignature, noteValues, nmaxNotesPerBar, noOfBars, note_range, left, right, bpm
            levels.append(par)

    if previous:
        index = levels.index(previous)
        return levels[i+1]
    else: # no previous TaskParameter, first Complexity Level
        return levels[0]

def thresholds(df):
    next_level = True
    for i in ["_right", "_left"]:
        if df['note_hold_time'+i] >= 1:
            next_level = False
        elif df['timing'+i] >= 0.2:
            next_level = False
        elif df['pitch'+i] >= 0.1:
            next_level = False
        elif df['n_missing_notes'+i] >= 0.1:
            next_level = False
        elif df['n_extra_notes'+i] >= 0.1:
            next_level = False
    if df['Summed_left'] >= 1.5:
        next_level = False
    elif df['Summed_right'] >= 1.5:
        next_level = False

    return next_level