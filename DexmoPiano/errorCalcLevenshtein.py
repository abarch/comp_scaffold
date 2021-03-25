"""
Calculates the error in regards to pitch and timing using an approach inspired
by the levenshtein distance.
"""

from collections import defaultdict, namedtuple
from dataclasses import dataclass
from pprint import pprint
import dataclasses

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    #{bcolors.WARNING}
    #{bcolors.ENDC}

class bcolors_empty:
    HEADER = ''
    OKBLUE = ''
    OKCYAN = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''



@dataclass
class NoteBase:
    def err_string(self, use_colors=True):
        if use_colors:
            bc = bcolors
        else:
            bc = bcolors_empty
        return f"{bc.WARNING}{self.__class__.__name__}{bc.ENDC}({fmt_dict(dataclasses.asdict(self))})"

    def lyr_string(self):
        return self.err_string(use_colors=False)

@dataclass
class NotePlayed(NoteBase):
    pitch : int
    velocity: int
    note_on_time : float
    note_on_time_relative : float
    note_hold_time : float
    
@dataclass
class NoteExpected(NotePlayed):
    pitch_target: int
    velocity_target: int
    note_on_time_target: float
    note_on_time_relative_target: float
    note_hold_time_target: float
    
    def err_string(self, use_colors=True):
        if use_colors:
            bc = bcolors
        else:
            bc = bcolors_empty
            
        err_strs = list()
        if self.pitch != self.pitch_target:
            err_strs.append(f"{bc.WARNING}Pitch{bc.ENDC}:\t\t{self.pitch-self.pitch_target:+d} [{self.pitch} - {self.pitch_target}]")
           
        hold_diff = self.note_hold_time - self.note_hold_time_target
        if abs(hold_diff) >= 0.1:
            err_strs.append(f"{bc.WARNING}Hold Time{bc.ENDC}:\t\t{hold_diff:+.2f} [{self.note_hold_time:.2f} - {self.note_hold_time_target:.2f}]")
            
            
        relative_on_diff = self.note_on_time_relative - self.note_on_time_relative_target
        if abs(relative_on_diff) >= 0.1:
            err_strs.append(f"{bc.WARNING}Rel On Time{bc.ENDC}:\t{relative_on_diff:+.2f} [{self.note_on_time_relative:.2f} - {self.note_on_time_relative_target:.2f}]")
            
        whitespace = " "*len("NoteExpected(")
        err_str = f"\n{whitespace}".join(err_strs)
        
        return f"NoteExpected({err_str})"
    
    def lyr_string(self):
        err_str = self.err_string(use_colors=False)
        only_core = err_str[err_str.find("(")+1:-1]
        
        return only_core or r"\null"

@dataclass
class NoteMissing(NoteBase):
    pitch_target: int
    velocity_target: int
    note_on_time_target: float
    note_on_time_relative_target: float
    note_hold_time_target: float
    
    def lyr_string(self):
        return "NoteMissing"
    
    
def fmt_dict(d):
    strs = list()
    for k, v in d.items():
        if type(v) != float:
            strs.append(f"{k}={v}")
        else:
            strs.append(f"{k}={v:.2f}")

    return ", ".join(strs)
@dataclass
class NoteExtra(NotePlayed):
    # def err_string(self):
    #     return f"{bcolors.WARNING}NoteExtra{bcolors.ENDC}({fmt_dict(dataclasses.asdict(self))})"
    pass


def viz_d(d):
    import numpy as np
    xs, ys = zip(*d.keys())
    v = np.zeros((max(xs)+2, max(ys)+2))
    
    for (x, y), val in d.items():
        v[x+1, y+1] = val
    
    print(v)


def damerau_levenshtein_distance(s1, s2, with_transposition=True, verbose=True):
    d = {}
    way = defaultdict(list)
    mapping = defaultdict(list)
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2):
        d[(-1,j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
                cost_way = ["-"]
            else:
                cost = 1
                cost_way = ["sub"]
                
                
            options = zip ([   
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                    ],#, ["del", "ins", "sub"], 
                [
                    way[(i-1,j)] + ["del"], # deletion
                    way[(i,j-1)] + ["ins"], # insertion
                    way[(i-1,j-1)] + cost_way ,
                    ],
                [
                    mapping[(i-1,j)] + [()], # deletion
                    mapping[(i,j-1)] + [(i,j)], # insertion
                    mapping[(i-1,j-1)] + [(i,j)] ,
                    ])
            best_option = sorted(options)[0]
            d[(i,j)] = best_option[0]
            way[(i,j)] = best_option[1]
            mapping[(i,j)] = best_option[2]
            if not with_transposition:
                continue
            
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                if d[i-2,j-2] + cost <= d[(i,j)]:
                    d[(i,j)] = d[i-2,j-2] + cost # transposition
                    way[(i,j)] = way[(i-2,j-2)] + ["trans1", "trans2"]

    
    
    distance = d[lenstr1-1,lenstr2-1]
    way_description = way[lenstr1-1,lenstr2-1]
    
    mapping = mapping[lenstr1-1,lenstr2-1]
    mapping = [t for t in mapping if len(t) > 0]
    mapping = {a:t for t, a in mapping}
    
    
    if verbose:
        # viz_d(d)
        print(distance)
        print(way_description)
        # print(mapping)
        
    return mapping


def note_info_list_add_debug(note_info_list):
    NoteInfoDebug = namedtuple("NoteInfoDebug", ["pitch", "velocity", 
                                                 "note_on_time", "note_off_time",
                                                 "time_after_anchor",
                                                 "note_hold_time"])
    
    debug_list = list()
    ## create anchor map
    ## anchor refers to a note in the actualNotes to which we calculate the timing
    # anchor_map = defaultdict(None)
    for i in range(len(note_info_list)):
        note_i = note_info_list[i]
        n = note_i
        note_hold_time = n.note_off_time - n.note_on_time
        for j in reversed(range(0, i)):
            note_j = note_info_list[j]
            # requirements: must anchor note must have been pressed some time before
            ANCH_THR = 0.24 #seconds
            # print(note_i, note_j)
            time_after_anchor = note_i.note_on_time - note_j.note_on_time
            if time_after_anchor >= ANCH_THR:
                debug_list.append(
                    NoteInfoDebug(n.pitch, n.velocity, n.note_on_time, n.note_off_time,
                                  time_after_anchor, note_hold_time))
                # anchor_map[i] = j
                break
        else:
            print("no anchor found for note at idx", i, note_i)
            debug_list.append(
                    NoteInfoDebug(n.pitch, n.velocity, n.note_on_time, n.note_off_time,
                                  0, note_hold_time))
            
    return debug_list

def computeError(targetNoteInfoList, actualNoteInfoList,
                 openface_data=None):
    target = sorted(targetNoteInfoList, key=lambda n:n.note_on_time)
    actual = sorted(actualNoteInfoList, key=lambda n:n.note_on_time)
    
    
    target_pitches = [-999] + [n.pitch for n in target]
    actual_pitches = [-999] + [n.pitch for n in actual]
    
    print("TP", target_pitches)
    print("AP", actual_pitches)
    
    mapping = damerau_levenshtein_distance(target_pitches, actual_pitches)
    
    ## clean up mapping from the -999 stuff
    del mapping[0]
    mapping = {k-1:v-1 for k, v in mapping.items()}
    print("MAP", mapping)
    
    rmap = dict() #defaultdict(list)
    for target_i in range(len(targetNoteInfoList)):
        rmap[target_i] = [actual_i for actual_i, ti in mapping.items() if 
                               ti == target_i]

    print("RMAP", rmap)    
    
    target_debug = note_info_list_add_debug(target)
    actual_debug = note_info_list_add_debug(actual)
    
    error_timing = 0
    error_note_hold_time   = 0
    error_pitch  = 0
    
    output_note_list = list()
    for t_i, a_i_list in rmap.items():
        t = target_debug[t_i]
        if len( a_i_list ) == 0:
            output_note_list.append(NoteMissing(t.pitch, t.velocity, 
                    t.note_on_time, t.time_after_anchor, t.note_hold_time))
            continue
        
        if len( a_i_list ) >= 1:
            a_i = a_i_list[-1]
            for extra_a_i in a_i_list[:-1]:
                a = actual_debug[extra_a_i]
                output_note_list.append(NoteExtra(a.pitch, a.velocity, 
                    a.note_on_time, a.time_after_anchor, a.note_hold_time))
        
            # continue using the non-extra note a_i
        
        if len( a_i_list ) == 1: #needed!
            a_i == a_i_list[0]
        
        
        a = actual_debug[a_i]
        
        pitch_diff = t.pitch - a.pitch
        if pitch_diff > 0:
            print("WRONG PITCH", t_i, t, a_i, a)
            error_pitch += 1
            
        hold_diff = t.note_hold_time - a.note_hold_time
        if abs(hold_diff) > 0:
            print("WRONG HOLD TIME", t_i, a_i, t.note_hold_time, a.note_hold_time)
            error_note_hold_time += abs(hold_diff)
            
        timing_diff = t.time_after_anchor - a.time_after_anchor
        if abs(timing_diff) > 0:
            print("WRONG TIMING", t_i, a_i, t.time_after_anchor, a.time_after_anchor)
            error_timing += abs(timing_diff)
    
        output_note_list.append(NoteExpected(a.pitch, a.velocity, a.note_on_time, a.time_after_anchor, a.note_hold_time, 
                                             t.pitch, t.velocity, t.note_on_time, t.time_after_anchor, t.note_hold_time))
    

    pprint(output_note_list)
    
    import shutil
    cwidth = shutil.get_terminal_size().columns
    
    print("NOTES".center(cwidth, "+"))
    for n in output_note_list:
        print(n.err_string())
    # pprint([n.err_string() for n in output_note_list])
    
    Error = namedtuple("Error", ["pitch", "note_hold_time", "timing"])
    
    #TODO missing missing notes / extra notes
    errors = Error(pitch=error_pitch, note_hold_time=error_note_hold_time, timing=error_timing)
    
    insert_lyrics_into_ly(output_note_list)
    
    try:
        note_list_to_plot(output_note_list, openface_data)
    except:
        import traceback
        traceback.print_exc()
    
    return output_note_list, errors

def simple_scale():
    from midiInput import NoteInfo
    
    notes = list()
    for pitch, start_time in zip(range(8), range(8)):
        notes.append(NoteInfo(pitch, 100, start_time*2, start_time*2+1))
        
    return notes

def drop_notes(actual, n_iter=2, verbose=True):
    import random
    for i in range(n_iter):
        idx = random.randint(0, len(actual)-1)
        dropped_note = actual.pop(idx)
        
        if verbose:
            print("Dropped", dropped_note)
    
    return actual

def repeat_notes(actual, n_iter=2, n_reps=1, verbose=True):
    import random
    already_repeated = set()
    for i in range(n_iter):
        idx = random.randint(0, len(actual)-1)
        note_to_repeat = actual[idx]
        while note_to_repeat in already_repeated:
            idx = random.randint(0, len(actual)-1)
            note_to_repeat = actual[idx]
        
        already_repeated.add(note_to_repeat)
        actual.pop(idx)
        
        if verbose:
            print(f"Repeating (x{n_reps})", note_to_repeat)
        
        n = note_to_repeat
        time_for_all_notes = n.note_off_time - n.note_on_time
        dt = time_for_all_notes / (n_reps +1) / 2
        
        for i in range(n_reps+1):
            ix2 = i*2
            new_note = NoteInfo(n.pitch, n.velocity, 
                            note_on_time =n.note_on_time + ix2*dt, 
                            note_off_time=n.note_on_time + (ix2+1)*dt)
            actual.insert(idx, new_note)
            already_repeated.add(new_note)
    
    return actual
       
def wrong_pitch(actual, n_iter=2, max_off=6, verbose=True):     
    import random
    # already_changed = set()
    for i in range(n_iter):
        idx = random.randint(0, len(actual)-1)
        note_to_change = actual.pop(idx)
        
        new_pitch = note_to_change.pitch + random.randint(1, max_off) * (-1**random.randint(0,1))
        
        n = note_to_change
        actual.insert(idx, NoteInfo(new_pitch, n.velocity, n.note_on_time, n.note_off_time))
        
        if verbose:
            print(f"Changed Pitch from {n.pitch} to {new_pitch} for", n)
    
    return actual

def add_pause(actual, n_iter=2, verbose=True):
    import random
    # already_changed = set()
    PAUSE_DUR = 3 #seconds
    for i in range(n_iter):
        idx = random.randint(1, len(actual)-2)
        
        for i in range(idx, len(actual)):
            n = actual[i]
            actual[i] = NoteInfo(n.pitch, n.velocity, 
                                 n.note_on_time+PAUSE_DUR, 
                                 n.note_off_time+PAUSE_DUR)
            
    return actual


def note_list_to_lyrics(note_list):
    lyrics = [r"\override LyricText.self-alignment-X = #1" + "\n"]
    buffer = list()
    
    markup_params = r"\hspace #2 \fontsize #-2 \box \pad-around #0.5"
    
    for note in note_list:
        if type(note) == NoteExtra:
            cols = note.lyr_string().split(", ")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            tmp_lyric = fr"{markup_params} \column {{ {joined_cols} }} \hspace #2 "
            
            buffer.append(tmp_lyric)
            continue
        
        buff_lyric = " ".join(buffer)
        buffer.clear()
        
        if type(note) == NoteExpected:
            cols = note.lyr_string().split("\n")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            lyric = fr"\markup{{ {buff_lyric} {markup_params} \column {{ {joined_cols} }} }}"
            
        
        if type(note) == NoteMissing:
            cols = note.lyr_string().split(", ")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            lyric = fr"\markup{{ {buff_lyric} {markup_params} \column {{ {joined_cols} }} }}"
        
        
        
        lyrics.append(lyric)
        
    
    all_lines =  "\n".join( lyrics)
    
    
    final_lyrics = fr"\addlyrics {{ {all_lines} }}"
    
    return final_lyrics


def note_list_to_plot(note_list, openface_data=None):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16,9))
    min_y = min([n.pitch for n in note_list if hasattr(n, "pitch")])
    for idx, note in enumerate(note_list):
        if type(note) == NoteExtra:
            cols = note.lyr_string().split(", ")
            x, y = note.note_on_time, note.pitch -min_y
            plt.scatter(x, y, c="b")
            plt.annotate("\n".join(cols), xy=(x, y), xytext=(x,-2 - (idx%5)),
                         arrowprops=dict(alpha=0.2),)
            
        
        elif type(note) == NoteExpected:
            cols = note.lyr_string().split("\n")
            x, y = note.note_on_time, note.pitch -min_y
            
            plt.scatter(x, y, c="b")
            plt.annotate("\n".join(cols), xy=(x, y), xytext=(x,-2 - (idx%5)),
                         arrowprops=dict(alpha=0.2),)
            
        
        if type(note) == NoteMissing:
            cols = note.lyr_string().split(", ")
            x, y = note.note_on_time_target, note.pitch_target -min_y
            plt.scatter(x, y, c="b")
            plt.annotate("\n".join(cols), xy=(x, y), xytext=(x,-2 - (idx%5)),
                         arrowprops=dict(alpha=0.2),)
        
    
    if openface_data is not None:
        # openface_data = openface_data.iloc[:-1,:]
        
        print(openface_data)
        
        from openface_data_acquisition import train_classifier_on_saved
        clf, target_classes, preprocess = train_classifier_on_saved()
    
        df = preprocess(openface_data)
        
        # prediction = clf.predict(df)
        prediction = clf.decision_function(df)
        
        # target_class = self.class_names[predicted_class]
        
        line_objects = plt.plot(openface_data.timestamp, prediction)
        plt.legend(line_objects, list(target_classes))
    
    # plt.legend()
    plt.ylim([-8,None])
    plt.show()


def insert_lyrics_into_ly(note_list):
    import shutil
    from pathlib import Path
    original_ly = Path("output/temp/output.ly")
    modified_ly = Path("output/temp/output_with_errors.ly")
    
    content = original_ly.read_text().splitlines()
    lyric_str = note_list_to_lyrics(note_list)
    
    # print(lyric_str)
    
    for idx, line in enumerate(content):
        if not r"\context Voice" in line:
            continue
        else:
            break
    else:
        print("(insert_lyrics_into_ly) LINE NOT FOUND!!!")
        return
    
    content.insert(idx+1, lyric_str)
    
    modified_ly.write_text("\n".join(content))
    
    import subprocess
    subprocess.run(['lilypond', '--png', '-o', modified_ly.parent, modified_ly], stderr=subprocess.DEVNULL)
    
    
    
    

if __name__ == "__main__":
    from midiInput import NoteInfo
    
    target_notes = simple_scale()
    actual_notes = target_notes.copy()
    
    drop_notes(actual_notes)
    # repeat_notes(actual_notes)
    # wrong_pitch(actual_notes)
    # add_pause(actual_notes)
    
    actual_notes = sorted(actual_notes, key=lambda n: n.note_on_time)
    
    print("TARGET_NOTES:")
    print(target_notes)
    print("ACTUAL_NOTES:")
    print(actual_notes)
    
    # print(computeError(target_notes, actual_notes))
    output_note_list, error = computeError(target_notes, actual_notes)
    
    # print(note_list_to_lyrics(output_note_list))
    # note_list_to_plot(output_note_list)
    insert_lyrics_into_ly(output_note_list)