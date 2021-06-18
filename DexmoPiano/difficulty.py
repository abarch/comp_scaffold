from DexmoPiano.task_generation.generator import TaskParameters
from DexmoPiano.task_generation.note_range_per_hand import NoteRangePerHand


def getTaskComplexity(previous=None):
    levels = []

    ranges = list(NoteRangePerHand)[1:]
    value = [1/2, 1/4]
    hands = ["right", "left"]
    right = False
    left = False

    note_range = NoteRangePerHand(3)
    parameters = TaskParameters((4, 4), [1 / 2, 1 / 4], 3, 7, note_range, False, True, 100)
    # timeSignature, noteValues, nmaxNotesPerBar, noOfBars, note_range, left, right, bpm
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
                right == True
            elif h == "left":
                left = True
            else:
                right = left = True
            par = TaskParameters((4,4), value, 3, 7, ranges[i], left, right, 100)
            levels.append(par)

    print(levels)
    if previous:
        index = levels.index(previous)
        return levels[i+1]
    else: # no previous TaskParameter, first Complexity Level
        # return levels[0]
        # TODO: Find bug, that below works and above does not, also check range and value
        return TaskParameters((4, 4), [1 / 2, 1 / 4], 3, 7, note_range, False, True, 100)
