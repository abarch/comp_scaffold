#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## check https://de.wikipedia.org/wiki/Unicodeblock_Notenschriftzeichen

from dataclasses import dataclass
from pprint import pprint
import dataclasses
from collections import namedtuple, OrderedDict

class unicode_notes:
    FULL_NOTE = "𝅝 "
    HALF_NOTE = "𝅗𝅥 "
    QUARTER_NOTE = "𝅘𝅥 "
    EIGHT_NOTE = "𝅘𝅥𝅮 "
    SIXTEEN_NOTE = "𝅘𝅥𝅯 "


def time_to_fraction(td, bpm, beats_per_measure=4):
    return td*bpm/(60 * beats_per_measure)
    

def fraction_to_single_note(fraction_of_measure, for_ly=False):
    rem_map = OrderedDict(
        FULL_NOTE = (1, "𝅝 "),
        HALF_NOTE = (1/2, "𝅗𝅥 "),
        QUARTER_NOTE = (1/4, "𝅘𝅥 "),
        EIGHT_NOTE = (1/8, "𝅘𝅥𝅮 "),
        # SIXTEEN_NOTE = (1/16, "𝅘𝅥𝅯 "),
        )
    
    if for_ly:
        for key, (d, note) in rem_map.items():
            rem_map[key] = (d, r"\fontsize #4 " + note)
    
    fraction_of_measure = abs(fraction_of_measure)
    
    if fraction_of_measure < 1/10:
        return ""
    
    diffs = [(abs(fraction_of_measure - frac), note) for frac, note in rem_map.values() ]
    
    return sorted(diffs)[0][1]
    

def fraction_to_notes(fraction_of_measure, levels=2, for_ly=False):
    rem_map = OrderedDict(
        FULL_NOTE = (1, "𝅝 "),
        HALF_NOTE = (1/2, "𝅗𝅥 "),
        QUARTER_NOTE = (1/4, "𝅘𝅥 "),
        EIGHT_NOTE = (1/8, "𝅘𝅥𝅮 "),
        # SIXTEEN_NOTE = (1/16, "𝅘𝅥𝅯 "),
        )
    
    if for_ly:
        for key, (d, note) in rem_map.items():
            rem_map[key] = (d, r"\fontsize #4 " + note)
    
    
    fraction_of_measure = abs(fraction_of_measure)
    
    if not for_ly:
        join_base = ""
    else:
        join_base = r"\hspace #0.1 "
    
    out_str = []
    for name, (divisor, note) in rem_map.items():
        div, fraction_of_measure = divmod(fraction_of_measure, divisor)
        if len(out_str) > 0 and int(div) == 0:
            return join_base.join(out_str)
        
        out_str += [note] * int(div)
        
        if len(set(out_str)) >= levels:
            return join_base.join(out_str)
    
    return join_base.join(out_str)
        

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
    
    # for easy copy pasting into f-strings
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

    def lyr_string(self, task_infos, lilypond=False, debug=False):
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
    
    def lyr_string(self, task_infos, lilypond=False, debug=False):
        if debug:
            err_str = self.err_string(use_colors=False)
            only_core = err_str[err_str.find("(")+1:-1]
            
            return only_core or r"\null"

        err_strs = list()
        if self.pitch != self.pitch_target:
            err_strs.append(f"Pitch:\t\t{self.pitch-self.pitch_target:+d}")
           
        relative_on_diff = self.note_on_time_relative - self.note_on_time_relative_target
        time_viz = fraction_to_single_note(
                    time_to_fraction(relative_on_diff, task_infos.bpm, task_infos.beats_per_measure),
                    for_ly = lilypond,
                    # levels=1
                    )
        if time_viz:
            if relative_on_diff > 0:
                text = "too late!"
            else: 
                text = "too early!"
            
            if lilypond:
                text = r" \hspace #1.5 "+ text
        
            err_strs.append(time_viz + text) 
           
        
        hold_diff = self.note_hold_time - self.note_hold_time_target
        time_viz = fraction_to_single_note(
                    time_to_fraction(hold_diff, task_infos.bpm, task_infos.beats_per_measure),
                    for_ly = lilypond,
                    # levels=1
                    )
        # if abs(hold_diff) >= 0.1:
        if time_viz:
            if hold_diff > 0:
                text = "too long!"
            else: 
                text = "too short!"
            
            if lilypond:
                text = r" \hspace #1.5 "+ text
        
            err_strs.append(time_viz + text)
            
        
        if lilypond and len(err_strs) == 0 :
            return r"\null"
        return "\n".join(err_strs) 

@dataclass
class NoteMissing(NoteBase):
    pitch_target: int
    velocity_target: int
    note_on_time_target: float
    note_on_time_relative_target: float
    note_hold_time_target: float
    
    def lyr_string(self, task_infos, lilypond=False, debug=False):
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


def get_anchor_map(target_notes):
    from collections import defaultdict
    anchor_map = defaultdict(lambda: (-1,0) )
    
    for i in range(len(target_notes)):
        note_i = target_notes[i]
        
        for j in reversed(range(0, i)):
            # print("j", j)
            note_j = target_notes[j]
            ANCH_THR = 0.1 #seconds ## not sure if needed / has to be greater 0
            time_after_anchor = note_i.note_on_time - note_j.note_on_time
            # print("j", j, time_after_anchor)
            if time_after_anchor > ANCH_THR:
                anchor_map[i] = (j, time_after_anchor)
                break
    
    # print("ANCHOR MAP", anchor_map)
    return anchor_map

def note_info_list_add_debug(note_info_list, mapping, anchor_map):
    NoteInfoDebug = namedtuple("NoteInfoDebug", ["pitch", "velocity", 
                                                 "note_on_time", "note_off_time",
                                                 "time_after_anchor",
                                                 "note_hold_time"])
    
    debug_list = list()
    # for t_i, a_i in enumerate(mapping):
    for i in range(len(note_info_list)):
        note_i = note_info_list[i]
        n = note_i
        note_hold_time = n.note_off_time - n.note_on_time
        
        if i not in mapping:
            ## can't calculate anchor for extra notes!
            debug_list.append(
            NoteInfoDebug(n.pitch, n.velocity, n.note_on_time, n.note_off_time,
                          -999, note_hold_time))
            continue
        
        t_i = mapping.index(i)
        
        anchor, anchor_td = anchor_map[t_i]
        if anchor == -1:
            time_after_anchor = 0
        elif mapping[anchor] == -1:
            time_after_anchor = anchor_td
        else:
            anchor_note = note_info_list[mapping[anchor]]
            time_after_anchor = n.note_on_time - anchor_note.note_on_time
        
        # print("TAA", i, anchor, mapping[anchor], time_after_anchor)
        
        debug_list.append(
            NoteInfoDebug(n.pitch, n.velocity, n.note_on_time, n.note_off_time,
                          time_after_anchor, note_hold_time))
            
    return debug_list

def get_explanation(target, actual, mapping,
                    task_infos,
                    inject_explanation=True,
                    openface_data=None,
                    plot=True,
                    ):
    anchor_map = get_anchor_map(target)
    target_debug = note_info_list_add_debug(target, list(range(len(target))), anchor_map)
    actual_debug = note_info_list_add_debug(actual, mapping, anchor_map)
    
    error_timing = 0
    error_note_hold_time   = 0
    error_pitch  = 0
    
    actual_notes_unused = set(range(len(actual_debug)))
    
    output_note_list = list()
    for t_i, a_i in enumerate(mapping):
        t = target_debug[t_i]
        if a_i == -1:
            output_note_list.append(NoteMissing(t.pitch, t.velocity, 
                    t.note_on_time, t.time_after_anchor, t.note_hold_time))
            continue
        
        actual_notes_unused.remove(a_i)
        a = actual_debug[a_i]
        
        pitch_diff = t.pitch - a.pitch
        if pitch_diff > 0:
            # print("WRONG PITCH", t_i, t, a_i, a)
            error_pitch += 1
            
        hold_diff = t.note_hold_time - a.note_hold_time
        if abs(hold_diff) > 0:
            # print("WRONG HOLD TIME", t_i, a_i, t.note_hold_time, a.note_hold_time)
            error_note_hold_time += abs(hold_diff)
            
        
        timing_diff = t.time_after_anchor - a.time_after_anchor
        if abs(timing_diff) > 0:
            # print("WRONG TIMING", t_i, a_i, t.time_after_anchor, a.time_after_anchor)
            error_timing += abs(timing_diff)
    
        output_note_list.append(NoteExpected(a.pitch, a.velocity, a.note_on_time, a.time_after_anchor, a.note_hold_time, 
                                             t.pitch, t.velocity, t.note_on_time, t.time_after_anchor, t.note_hold_time))
    
    for unused_a_i in actual_notes_unused:
        a = actual_debug[unused_a_i]
        output_note_list.append(NoteExtra(a.pitch, a.velocity, 
                    a.note_on_time, a.time_after_anchor, a.note_hold_time))

    def get_note_on(note):
        if hasattr(note, "note_on_time"):
            return note.note_on_time
        if hasattr(note, "note_on_time_target"):
            return note.note_on_time_target
        raise Exception("Note type can't be sorted bc no note on.")
    output_note_list = sorted(output_note_list, key=get_note_on)

    # pprint(output_note_list)
    
    # import shutil
    # cwidth = shutil.get_terminal_size().columns
    # print("NOTES".center(cwidth, "+"))
    # for n in output_note_list:
    #     print(n.err_string())
    
    
    # ONE FOR EACH HAND?
    Error = namedtuple("Error", ["pitch", "note_hold_time", "timing",
                                 "n_missing_notes", "t_missing_notes",
                                 "n_extra_notes", "t_extra_notes",
                                 ])
    
    #TODO missing missing notes / extra notes
    errors = Error(pitch=error_pitch, note_hold_time=error_note_hold_time, timing=error_timing,
                   n_missing_notes=mapping.count(-1),
                   t_missing_notes=sum(
                       target_debug[i].note_hold_time for i in range(len(target_debug))
                       if mapping[i] == -1),
                   n_extra_notes = len(actual_notes_unused),
                   t_extra_notes = sum(actual_debug[a].note_hold_time for a in actual_notes_unused)
                   )
    
    
    if inject_explanation:
        insert_lyrics_into_ly(output_note_list, task_infos)
    
    if plot:
        try:
            note_list_to_plot(output_note_list, task_infos, openface_data)
        except:
            import traceback
            traceback.print_exc()
    
    return output_note_list, errors

#lyr_string(self, task_infos, lilypond=False, debug=False):

def note_list_to_lyrics(note_list, task_infos, lilypond, debug=False):
    lyrics = [r"\override LyricText.self-alignment-X = #1" + "\n"]
    buffer = list()
    
    markup_params = r"\hspace #2 \fontsize #-2 \box \pad-around #0.5"
    
    for note in note_list:
        if type(note) == NoteExtra:
            cols = note.lyr_string(task_infos, lilypond=lilypond, debug=debug).split(", ")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            tmp_lyric = fr"{markup_params} \column {{ {joined_cols} }} \hspace #2 "
            
            buffer.append(tmp_lyric)
            continue
        
        buff_lyric = " ".join(buffer)
        buffer.clear()
        
        if type(note) == NoteExpected:
            cols = note.lyr_string(task_infos, lilypond=lilypond, debug=debug).split("\n")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            lyric = fr"\markup{{ {buff_lyric} {markup_params} \column {{ {joined_cols} }} }}"
            
        
        if type(note) == NoteMissing:
            cols = note.lyr_string(task_infos, lilypond=lilypond, debug=debug).split(", ")
            joined_cols = "\n".join([fr"\line {{ {c} }}" for c in cols])
            lyric = fr"\markup{{ {buff_lyric} {markup_params} \column {{ {joined_cols} }} }}"
        
        
        
        lyrics.append(lyric)
        
    
    all_lines =  "\n".join( lyrics)
    
    
    final_lyrics = fr"\addlyrics {{ {all_lines} }}"
    
    return final_lyrics


def note_list_to_plot(note_list, task_infos, openface_data=None, debug=False):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16,9))
    min_y = min([n.pitch for n in note_list if hasattr(n, "pitch")])
    for idx, note in enumerate(note_list):
        if type(note) == NoteExtra:
            cols = note.lyr_string(task_infos, lilypond=False, debug=debug).split(", ")
            x, y = note.note_on_time, note.pitch -min_y
            plt.scatter(x, y, c="b")
            plt.annotate("\n".join(cols), xy=(x, y), xytext=(x,-2 - (idx%5)),
                         arrowprops=dict(alpha=0.2),)
            
        
        elif type(note) == NoteExpected:
            cols = note.lyr_string(task_infos, lilypond=False, debug=debug).split("\n")
            x, y = note.note_on_time, note.pitch -min_y
            
            plt.scatter(x, y, c="b")
            plt.annotate("\n".join(cols), xy=(x, y), xytext=(x,-2 - (idx%5)),
                         arrowprops=dict(alpha=0.2),)
            
        
        if type(note) == NoteMissing:
            cols = note.lyr_string(task_infos, lilypond=False, debug=debug).split(", ")
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


def insert_lyrics_into_ly(note_list, task_infos):
    # import shutil
    from pathlib import Path
    original_ly = Path("output/temp/output.ly")
    modified_ly = Path("output/temp/output_with_errors.ly")
    
    content = original_ly.read_text().splitlines()
    lyric_str = note_list_to_lyrics(note_list, task_infos, lilypond=True)
    
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
    