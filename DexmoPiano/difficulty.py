from DexmoPiano.task_generation.generator import TaskParameters
from DexmoPiano.task_generation.note_range_per_hand import NoteRangePerHand


def getTaskComplexity(previous=None):
    levels = []

    print("Notes Ranges", list(NoteRangePerHand)[2:])
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
    print("These are all levels: ", levels)
    if previous:
        print("previous Level in difficulty:", previous)
        for index in range(len(levels)):
            if str(levels[index]) == str(previous):
                print("this Level is the same:", index, levels[index])
                print("this is the new Level:", levels[index+1])
                return levels[index+1]
    else: # no previous TaskParameter, first Complexity Level
        return levels[0]

def thresholds(df):
    next_level = True
    for i in ["_right", "_left"]:
        if df['note_hold_time'+i] >= 2:
            print("Hold Time Error")
            next_level = False
        elif df['timing'+i] >= 0.2:
            print("Timing Error")
            next_level = False
        elif df['pitch'+i] >= 0.1:
            print("Pitch Error")
            next_level = False
        elif df['n_missing_notes'+i] >= 0.1:
            print("Missing Notes Error")
            next_level = False
        elif df['n_extra_notes'+i] >= 0.1:
            print("Extra Notes Error")
            next_level = False
    if df['Summed_left'] >= 2.1:
        print("Summed Left Error")
        next_level = False
    elif df['Summed_right'] >= 2.1:
        print("Summed Right Error")
        next_level = False

    return next_level