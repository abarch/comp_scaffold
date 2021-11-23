

from task_generation.generator import TaskParameters
from task_generation.note_range_per_hand import NoteRangePerHand
import networkx  as nx


# this generates the graph with max four notes in the left, four notes in the right hand and either   
# 0 means 1 note, or one hand. "1" hand means either alternating or bimanual tasks
# 4,4
def exp_graph(dim=(2,4,4)):
    G = nx.grid_graph(dim)
    #G= nx.grid_graph(dim=(2,3,4,5))
    for line in nx.generate_adjlist(G):
        print(line)

    #print (G.nodes())
    # import matplotlib.pyplot as plt
    # # nx.spring_layout
    #
    # nx.draw(G)
    # plt.draw()
    # plt.show()
    return G

# given a tuple of the above dimension - create a task
def make_task_from_node(node =(1,1,0)):
    #rhythmic resolution is constantly at the same level
    value = [1/2, 1/4]

    notes_left= node[0]
    notes_right=node[1]
    hand_descr= node[2]


    ranges = list(NoteRangePerHand)[1:]
    #print ("note ranges", ranges)

    if hand_descr==0 and notes_left > 0 and notes_right > 0:
        # testing one case
        alternating = True
        left = True
        right=True

    elif hand_descr==1 and notes_left > 0 and notes_right> 0:
        alternating = False
        left = True
        right = True

    elif notes_left == 0 and notes_right ==0: # a one-time case
        # default task
        notes_right = 1
        alternating = False
        right = True
        left = False
    else:
        alternating = False
        left = False  if notes_left ==0  else  True
        right = False if notes_right== 0 else  True
    from task_generation.generator import generate_task
    par = TaskParameters((4,4), value.copy(), 3, 9,  ranges[notes_right], ranges[notes_left], left, right, alternating, 100)
    #print (par)
    #generate_task(par)
    return par

def getTasks():
    levels = []
    nodes = []
    G = exp_graph()
    for node in G.nodes():
        par= make_task_from_node(node)
        levels.append(par)
        nodes.append(node)
    return levels,nodes

def thresholds(df):
    """
    Checks the performance errors against the thresholds and returns a boolean value if the player should play the next
    complexity level or start learning during the difficulty adjustment.

    @param df: errors of practice opportunity
    @return: True/False for next_level
    """
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

#getTaskComplexity()

    # elif hand_descr==1

        # timeSignature: tuple = (4, 4)
        # noteValues: list = dc.field(default_factory=lambda: [1 / 2, 1 / 4])
        # maxNotesPerBar: int = 3
        # noOfBars: int = 7
        # note_range_right: NoteRangePerHand = NoteRangePerHand.TWO_NOTES
        # # FIXME: debug
        # note_range_left: NoteRangePerHand = NoteRangePerHand.ONE_NOTE
        # left: bool = False
        # right: bool = True
        # alternating: bool = True
        # bpm: float = 100
#exp_graph()


#
# from task_generation.generator import TaskParameters
# from task_generation.note_range_per_hand import NoteRangePerHand
#
# # FIXME: this needs to be refactored!
#
# def getTaskComplexity(previous=None):
#     """
#     Returns the TaskParameters and Index of a level based on the previous level. If no previous level has been given,
#     the first level is returned.
#     @param previous: previous TaskParameters
#     @return: TaskParameter for new level
#     @return: index of new level
#     """
#     levels = []

#
#     #print("Notes Ranges", list(NoteRangePerHand)[2:])
#     # use all NoteRanges starting with two notes per hand
#     ranges = list(NoteRangePerHand)[2:]
#     # start with quarter and half notes
#     value = [1/2, 1/4]
#     hands = ["right", "left", "both"]
#     sim = False
#
#
#     for i in range(len(ranges)):
#         if i == 1:
#             value.append(1)
#         if i == 2:
#             value.append(1/8)
#         if i == 3:
#             sim = True
#         if i == 4:
#             value.append(1/16)
#         for h in hands:
#             if h == "right":
#                 right = True
#                 left = False
#                 alternating = False
#             elif h == "left":
#                 left = True
#                 right = False
#                 alternating = False
#             else:
#                 right = left = True
#                 if not sim:
#                     alternating = True
#
#             par = TaskParameters((4,4), value.copy(), 3, 7, ranges[i], ranges[i], left, right, alternating, 100)
#
#             # timeSignature, noteValues, nmaxNotesPerBar, noOfBars, note_range, left, right, bpm
#             levels.append(par)
#     #print("These are all levels: ", levels)
#     if previous:
#         #print("previous Level in difficulty:", previous)
#         for index in range(len(levels)):
#             if str(levels[index]) == str(previous):
#                 #print("this Level is the same:", index, levels[index])
#                 #print("this is the new Level:", levels[index+1])
#                 return levels[index+1], index+1
#         return None
#     # no previous TaskParameter, first Complexity Level
#     else:
#         return levels[0], 0
#
# def thresholds(df):
#     """
#     Checks the performance errors against the thresholds and returns a boolean value if the player should play the next
#     complexity level or start learning during the difficulty adjustment.
#
#     @param df: errors of practice opportunity
#     @return: True/False for next_level
#     """
#     next_level = True
#     for i in ["_right", "_left"]:
#         if df['note_hold_time'+i] >= 2:
#             print("Hold Time Error")
#             next_level = False
#         elif df['timing'+i] >= 0.2:
#             print("Timing Error")
#             next_level = False
#         elif df['pitch'+i] >= 0.1:
#             print("Pitch Error")
#             next_level = False
#         elif df['n_missing_notes'+i] >= 0.1:
#             print("Missing Notes Error")
#             next_level = False
#         elif df['n_extra_notes'+i] >= 0.1:
#             print("Extra Notes Error")
#             next_level = False
#     if df['Summed_left'] >= 2.1:
#         print("Summed Left Error")
#         next_level = False
#     elif df['Summed_right'] >= 2.1:
#         print("Summed Right Error")
#         next_level = False
#
#     return next_level