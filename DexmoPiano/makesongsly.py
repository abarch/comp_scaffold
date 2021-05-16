import subprocess
import os
import platform
from PIL import Image

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

def make_song(song_num,bpm):
    fn = 'songs/song' + str(song_num) + '.ly'
    output = 'songs/song' + str(song_num)
    song = songs[song_num-1]
    write_song(fn,song,bpm)
    subprocess.run(['lilypond', '--png', '-o', output+'_tmp', fn])#, stderr=subprocess.DEVNULL)
    # TODO: this shouldn't have a fixed size
    im = Image.open(output+'_tmp.png') 
    im1 = im.crop((0,0,800,100))
    im1.save(output+'.png')
    os.remove(output+'_tmp.png')
   
#    subprocess.run(['/usr/bin/convert',output+'_tmp.png',
#        '-crop','800x100+60+0',output+'.png'])

    if platform.system()=='Windows':
        os.replace(output+'_tmp.mid',output+'.midi')
    else:
        os.replace(output+'_tmp.midi',output+'.midi')
    
def write_song(fn,song,bpm):
    with open(fn, 'w') as f:
        f.write('\\version "2.20.0"\n')
        f.write("\\header {\n")
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
        f.write("\\midi {\\tempo 4 = " + str(bpm) + "}\n")
        f.write("}\n")

if __name__ == "__main__":

    bpm = 60

    for k in range(10):
        make_song(k+1,bpm)
