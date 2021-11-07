from task_generation.generator import TaskParameters
from task_generation.note_range_per_hand import NoteRangePerHand

import networkx as nx
import copy

from dataclasses import dataclass

@dataclass
class Node:
    """
    @param note_range : note ranges for the left and the right hands respectively
    @param rhythm_res : the type of rhythmic complexity we employ
    """
    note_range_left :int  = 0
    note_range_right : int = 1

    rhythm_res_left :int = 0
    rhythm_res_right : int = 1/4
    alternating: bool  = False

    def inc_range_left(self):
        self.note_range_left +=1
        return self
    def inc_range_right(self):
        self.note_range_right +1
        return self




G = nx.DiGraph()

# add root
G.add_node(0, note_range_right = 0, rhythm_res_right= 0, note_range_left =0, rhythm_res_left =0)


def next_level(index):
    highest = 1

    n=G.nodes[index]

    for  key,value in  n.items():
        print (key,value)
        if key == "note_range_right":
            G.add_node(highest, note_range_left = value+1, rhythm_res_left=n['rhythm_res_left'],
                       note_range_right=n['note_res_right'], rhythm_res_right=n['note_res_right'])
            G.add_edge(index, highest)
            highest += 1

next_level(0)

G = nx.grid_graph(4)
for line in nx.generate_adjlist(G):
    print(line)

import matplotlib.pyplot as plt

nx.draw(G)
plt.draw()
plt.show()
