from tkinter import *
from  PIL import Image, ImageTk

# Make the lilypond songs
songs = ["\\relative c'{\\numericTimeSignature c2 c e e c c e e g g e e c c c1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c2 e g g e c g'1 c,2 e g e c g' c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c2 g' e g c, e g1 c,2 e4 c g'2 g c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c2 c4 e c2 e g g4 e c2 e g e4 c e2 g4 e e2 g4 e c1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c2 g'4 c, e2 g e4 g c,2 e e g4 e g2 e2 c g'4 c, g'2 c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c e c e g2 e4 c g'2 c, e1 g4 e g e c2 e4 g e2 g c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c g' c, e g e g2 e4 g c,2 g' e e4 c g' c, e2 c4 e g c, e g c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c2 g' e4 g2 c,4 g'2 c, e1 g4 e g c, e2 g4 c, e g2 e4 c1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c e c g' e c2 g'4 e c g' e c g' e2 g4 e g c, g' c, e2 c4 e2 g4 c,1 \\bar \"|.\"}",
         "\\relative c'{\\numericTimeSignature c g'2 e4 g c, e2 g4 c, e c g' e2 g4 e c g' e c g' e2 c4 g'2 e4 c1 \\bar \"|.\"}"]

songDir = './songs/'

class VisualNotes():
    # class for creating and updating notes as visual vertical bars.

    def __init__(self,canvas, start_pos_x=50,start_pos_y=50,key_width=15,key_length=50,quarter_len=15):

        self.canvas = canvas
        self.mode = "wait" # "wait" - wait for correct note. "cont" - draw continuously the pressed note.
        self.start_pos_x = start_pos_x
        self.start_pos_y = start_pos_y
        self.key_width = key_width
        self.key_length = key_length
        self.quarter_len = quarter_len
        self.pitch_list = []
        self.duration_list = []
        self.midi2int = {"60": 1, "62": 2, "64": 3, "65": 4, "67": 5, "69": 6, "70": 7, "71": 8}
        self.current_pitch = []
        self.current_wait_for_note = 0
        self.current_wait_for_note_y = self.start_pos_y + self.key_length
        self.current_wait_for_note_x = 200

    def set_mode(self,mode):
        self.mode = mode

    def set_notes(self, pitch_list, duration_list):
        self.pitch_list = pitch_list
        self.duration_list = duration_list

    def set_tempo(self, tempo):
        self.tempo = tempo

    def draw_notes(self):
        # draw visual notes
        current_y = self.start_pos_y + self.key_length
        for k in range(len(self.pitch_list)):
            current_x = (self.pitch_list[k] - 1) * self.key_width
            print(current_x, current_x + self.key_width, current_y, current_y + self.quarter_len * self.duration_list[k])
            self.canvas.create_rectangle(self.start_pos_x + current_x, current_y, self.start_pos_x + current_x + self.key_width,
                                    current_y + self.quarter_len * self.duration_list[k], fill='lightblue')
            current_y += self.quarter_len * self.duration_list[k]
            # current_y = current_y + duration_list[k]

    def draw_keyboard(self, key_pressed):

        # draw keyboard
        for k in range(17):  # white keys
            self.canvas.create_rectangle(self.start_pos_x + k * self.key_width, self.start_pos_y, self.start_pos_x + (k + 1) * self.key_width,
                                    self.start_pos_y + self.key_length, fill='white')
            if key_pressed and k == self.midi2int[str(key_pressed)] - 1:
                self.canvas.create_rectangle(self.start_pos_x + k * self.key_width, self.start_pos_y, self.start_pos_x + (k + 1) * self.key_width,
                                        self.start_pos_y + self.key_length, fill='orange')
            if k % 7 in [1, 2, 4, 5, 6]:  # black keys
                self.canvas.create_rectangle(self.start_pos_x + k * self.key_width - 0.2 * self.key_width, self.start_pos_y,
                                        self.start_pos_x + k * self.key_width + 0.2 * self.key_width, self.start_pos_y + 0.66 * self.key_length,

                                        fill='black')
    def init_v_cursor(self):
        # initialize vertical cursor
        self.v_cursor = self.canvas.create_line(self.start_pos_x-25, self.start_pos_y + self.key_length, self.start_pos_x-10, self.start_pos_y + self.key_length, width=5, fill='red')

    def init_h_cursor(self, x_pos, y_pos, h_quarter_len):
        # initialize horizontal cursor

        self.h_cursor_x = x_pos
        self.h_cursor_y = y_pos
        self.h_quarter_len = h_quarter_len
        self.current_wait_for_note_x = x_pos

        self.h_cursor = self.canvas.create_line(self.h_cursor_x, self.h_cursor_y, self.h_cursor_x, self.h_cursor_y+20, width = 5, fill='red')


    # def draw_actual_notes(self, actual_notes):
    #     # draw actual notes
    #
    #     for k in range(len(actual_notes)):
    #         canvas.create_rectangle(self.start_pos_x + self.key_width * (self.midi2int[str(actual_notes[k][0])] - 1),
    #                                 self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len * actual_notes[k][2],
    #                                 self.start_pos_x + self.key_width * self.midi2int[str(actual_notes[k][0])],
    #                                 self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len * actual_notes[k][3],
    #                                 fill='red', tag='notes')

    def update_key_pressed(self, pitch, current_ts):
        self.draw_keyboard(pitch)
        if self.mode == "cont":
            self.update_key_pressed_cont(pitch, current_ts)
        elif self.mode == "wait":
            self.wait_for_note(pitch)



    def update_key_pressed_cont(self, pitch, current_ts):
        if pitch != self.current_pitch:
            self.current_pitch = pitch
            self.start_ts = current_ts
            self.current_bar = self.canvas.create_rectangle(self.start_pos_x + self.key_width * (self.midi2int[str(self.current_pitch)] - 1),
                                    self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len *
                                    self.start_ts,
                                    self.start_pos_x + self.key_width * self.midi2int[str(self.current_pitch)],
                                    self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len *
                                    current_ts,
                                    fill='red', tag='notes')

    def update_key_released(self, pitch, current_ts):
        self.current_pitch = False
        self.start_ts = False
        self.draw_keyboard(False)

    def update_actual_notes(self, current_ts):
        # update vertical cursor
        self.canvas.coords(self.v_cursor, self.start_pos_x-25, self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len * current_ts, self.start_pos_x-10, self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len * current_ts)

        # update horizontal cursor
        self.canvas.coords(self.h_cursor, self.h_cursor_x+ (self.tempo / 60.0) * self.h_quarter_len * current_ts, self.h_cursor_y, self.h_cursor_x+ (self.tempo / 60.0) * self.h_quarter_len * current_ts, self.h_cursor_y+20)

            # update current pitch box
        if self.current_pitch:
            self.canvas.coords(self.current_bar, self.start_pos_x + self.key_width * (self.midi2int[str(self.current_pitch)] - 1),
                                    self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len *
                                    self.start_ts,
                                    self.start_pos_x + self.key_width * self.midi2int[str(self.current_pitch)],
                                    self.start_pos_y + self.key_length + (self.tempo / 60.0) * self.quarter_len *
                                    current_ts)


    def init_wait_for_note(self):
        # initialize cursors to be on the first note.

        self.current_wait_for_note_y = self.start_pos_y+ self.key_length #+ self.quarter_len * self.duration_list[0]
        #self.current_wait_for_note_x = self.h_quarter_len * self.duration_list[0]
        # initialize index of current note
        self.current_wait_for_note = 0


        # update vertical cursor
        self.canvas.coords(self.v_cursor, self.start_pos_x - 25,
                           self.current_wait_for_note_y,
                           self.start_pos_x - 10,
                           self.current_wait_for_note_y)

        # update horizontal cursor
        self.canvas.coords(self.h_cursor, self.current_wait_for_note_x,
                           self.h_cursor_y, self.current_wait_for_note_x,
                           self.h_cursor_y + 20)

    def is_wait_for_note_done(self):
        # return true if all notes have been played
        return self.current_wait_for_note == len(self.pitch_list)

    def wait_for_note(self, pitch):
        print(pitch, self.pitch_list[self.current_wait_for_note])
        if self.midi2int[str(pitch)] == self.pitch_list[self.current_wait_for_note]:
            print("success")
            # draw visual notes

            current_x = (self.pitch_list[self.current_wait_for_note] - 1) * self.key_width
            print(current_x, current_x + self.key_width, self.current_wait_for_note_y,
                  self.current_wait_for_note_y + self.quarter_len * self.duration_list[self.current_wait_for_note])
            self.canvas.create_rectangle(self.start_pos_x + current_x, self.current_wait_for_note_y,
                                         self.start_pos_x + current_x + self.key_width,
                                         self.current_wait_for_note_y + self.quarter_len * self.duration_list[self.current_wait_for_note], fill='red', tag='notes')
         #   self.current_wait_for_note_y += self.quarter_len * self.duration_list[self.current_wait_for_note]
         #   self.current_wait_for_note += 1

            # update cursors

            # update vertical cursor
            self.canvas.coords(self.v_cursor, self.start_pos_x - 25,
                               self.current_wait_for_note_y,
                               self.start_pos_x - 10,
                               self.current_wait_for_note_y)

            # update horizontal cursor
            self.canvas.coords(self.h_cursor, self.current_wait_for_note_x ,
                               self.h_cursor_y, self.current_wait_for_note_x,
                               self.h_cursor_y + 20)

            # update time and next note
            self.current_wait_for_note_y += self.quarter_len * self.duration_list[self.current_wait_for_note]
            self.current_wait_for_note_x += self.h_quarter_len * self.duration_list[self.current_wait_for_note]
            self.current_wait_for_note += 1

        else:
            print("fail")

    def create_pitch_duration_lists(self,notes_str):
        pitch_list = []
        duration_list = []
        notes = notes_str.split()
        last_duration = 4;
        for note in notes:
            pitch, duration = parse_note(note, last_duration)
            pitch_list.append(pitch)
            duration_list.append(duration)
            print(pitch, duration)
            last_duration = duration
        return pitch_list, duration_list

    def clear_notes(self):
        self.canvas.delete("notes")
        self.current_pitch = []
        self.current_wait_for_note = 0
        self.current_wait_for_note_y = self.start_pos_y + self.key_length
        self.current_wait_for_note_x = self.h_cursor_x

def parse_note(note, last_duration = 4):
    notes2int = {"c":1, "d":2, "e":3, "f":4, "g":5, "a":6, "b":7}
    duration = last_duration;
    pitch = notes2int[note[0]]
    if len(note)>1:
        if note[1] == "'":
            pitch += 8
        elif note[1] == ",":
            pitch -= 8
        elif note[-1].isnumeric():
            duration = int(note[-1])
    return pitch, duration

def create_pitch_duration_lists(notes_str):
    pitch_list = []
    duration_list = []
    notes = notes_str.split()
    last_duration = 4;
    for note in notes:
        pitch, duration = parse_note(note, last_duration)
        pitch_list.append(pitch)
        duration_list.append(duration)
        print(pitch, duration)
        last_duration = duration
    return pitch_list, duration_list


def draw_keyboard(start_pos_x, start_pos_y, key_width, key_length,quarter_len, tempo, pitch_list, duration_list, actual_notes, key_pressed,  canvas):

    midi2int = {"60": 1, "62": 2, "64": 3, "65": 4, "67": 5, "69": 6, "70": 7, "71": 8}

    # upper left corner
    start_pos_x = start_pos_x
    start_pos_y = start_pos_y
    key_length = key_length

    # draw keyboard
    for k in range(17): # white keys
        canvas.create_rectangle(start_pos_x+k*key_width, start_pos_y, start_pos_x+(k+1)*key_width, start_pos_y+key_length , fill='white')
        if key_pressed and k == midi2int[str(key_pressed)]-1:
            canvas.create_rectangle(start_pos_x + k * key_width, start_pos_y, start_pos_x + (k + 1) * key_width,
                                    start_pos_y + key_length, fill='orange')
        if k % 7 in [1,2,4,5,6]: # black keys
            canvas.create_rectangle(start_pos_x+k*key_width-0.2*key_width, start_pos_y, start_pos_x+k*key_width+0.2*key_width, start_pos_y+0.66*key_length, fill='black')

    # draw visual notes
    current_y = start_pos_y + key_length
    for k in range(len(pitch_list)):
        current_x = (pitch_list[k]-1) * key_width
        print(current_x, current_x + key_width, current_y, current_y + quarter_len * duration_list[k])
        canvas.create_rectangle(start_pos_x+current_x, current_y, start_pos_x+current_x + key_width, current_y + quarter_len * duration_list[k], fill='lightblue')
        current_y += quarter_len * duration_list[k]
        # current_y = current_y + duration_list[k]

    # draw actual notes

    for k in range(len(actual_notes)):
        canvas.create_rectangle(start_pos_x+key_width*(midi2int[str(actual_notes[k][0])]-1), start_pos_y + key_length + (tempo/60.0)*quarter_len*actual_notes[k][2], start_pos_x+ key_width*midi2int[str(actual_notes[k][0])], start_pos_y + key_length + (tempo/60.0)*quarter_len*actual_notes[k][3], fill='red')



def create_visual_notes(pitch_list, duration_list,canvas):
    key_width = 15
    quarter_len = 15
    current_x = pitch_list[0]*key_width
    current_y = 10
    for k in range(len(pitch_list)):
        current_x = pitch_list[k] * key_width
        print(current_x, current_x+key_width, current_y, current_y+quarter_len*duration_list[k])
        canvas.create_rectangle(current_x, current_y, current_x+key_width, current_y+quarter_len*duration_list[k])
        current_y += quarter_len*duration_list[k]
        # current_y = current_y + duration_list[k]


#
# root = Tk()
# root.title("Piano test")
# canvas = Canvas(root, width=750, height = 800, bg='white')
#
# vnotes = VisualNotes(canvas=canvas)
# canvas.pack()
# vnotes.draw_keyboard("62")
# pitch_list, duration_list = create_pitch_duration_lists("c2 c e e c c e e g g e e c c c1")
# vnotes.set_notes(pitch_list, duration_list)
# vnotes.draw_notes()
# actual_notes = [[60, 25, 0,1,0], [62, 25, 2,2.5,0]]
# vnotes.set_tempo(60)
# vnotes.update_key_pressed(60,0)
# vnotes.update_actual_notes(3)
# vnotes.update_key_released(60,3)
# vnotes.update_key_pressed(62, 4)
# vnotes.update_actual_notes(6)
#
# #vnotes.draw_actual_notes(actual_notes)
#
# root.mainloop()
# pitch_list, duration_list = create_pitch_duration_lists("c2 c e e c c e e g g e e c c c1")
# print(create_pitch_duration_lists("c2 c e e c c e e g g e e c c c1"))
# #pitch_list, duration_list = create_pitch_duration_lists("c2 e g g e c g'1 c,2 e g e c g' c,1")
# actual_notes = [[60, 25, 0,1,0], [62, 25, 2,2.5,0]]
# draw_keyboard(start_pos_x=50,start_pos_y=50,key_width=15,key_length=50,quarter_len=15,tempo=60, pitch_list=pitch_list, duration_list=duration_list,actual_notes=actual_notes,key_pressed=60, canvas=canvas)
# #create_visual_notes(pitch_list=pitch_list, duration_list=duration_list,canvas=canvas)
# canvas.pack()
# # Set the resolution of window
# root.geometry("1500x1000")
# root.mainloop()

#    alien1 = canvas.create_oval(20 + 100, 260 - 130, 40 + 100, 300 - 130, outline='white', fill='yellow')
 #   canvas.pack()

# def make_song(song_num,bpm):
#     fn = 'songs/song' + str(song_num) + '.ly'
#     output = 'songs/song' + str(song_num)
#     song = songs[song_num-1]
#     write_song(fn,song,bpm)
#     subprocess.run(['lilypond', '--png', '-o', output+'_tmp', fn])#, stderr=subprocess.DEVNULL)
#     # TODO: this shouldn't have a fixed size
#     im = Image.open(output+'_tmp.png')
#     im1 = im.crop((0,0,800,100))
#     im1.save(output+'.png')
#     os.remove(output+'_tmp.png')