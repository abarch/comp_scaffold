import subprocess
import os
import glob
import platform
import sys
from pathlib import Path
from PIL import Image

# Make the lilypond songs

songDir = './songs/'


def make_song(song_name, bpm):
    base = songDir + song_name

    song = Path(base + '.lypart').read_text()

    write_song(base + '.ly', song, bpm)
    subprocess.run(['lilypond', '--png', '-o', base, base])#, stderr=subprocess.DEVNULL)

    # Remove the temp files
    filelist = glob.glob(base + '-*')
    print(filelist)
    for filepath in filelist:
        try:
            os.remove(filepath)
        except:
            print("Error while deleting file : ", filepath)

def write_song(fn, song, bpmsong):
    with open(fn, 'w') as f:
        f.write('\\version "2.20.0"\n')
        f.write("\\header {\n")
        f.write("\\include \"lilypond-book-preamble.ly\"\n")
#        f.write("\\paper {oddFooterMarkup =  ##f }\n")
        f.write('   tagline = "" % removed\n')
        f.write(" }\n")
        f.write("\\score {\n")
        f.write(" {\n")
        f.write("  " + song + "\n")
        f.write("}\n")
        f.write("\\layout {\n")
        f.write("  \\context {\n")
        f.write("      \\Score \n")
        f.write("      proportionalNotationDuration =  #(ly:make-moment 1/5)\n")
        f.write(" }\n }\n")
        f.write("\\midi {\\tempo 4 = " + str(bpmsong) + "}\n")
        f.write("}\n")


if __name__ == "__main__":

    n = len(sys.argv)
    if n < 3:
        bpm = 60
    else:
        bpm = int(sys.argv[2])

    if n < 1:  # Do all the sample songs
        for k in range(10):
            make_song('song' + str(k+1), bpm)
    else:
        songname = sys.argv[1]
        make_song(songname, bpm)
