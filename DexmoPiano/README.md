# Visual Attention flavor of DexmoPiano
If there are any questions/problems, contact Sören.

## Contributing Training Data for the classificator:

### Making sure everything is set up correctly:
1. You need a webcam (external preferred)
2. You need openface (https://github.com/TadasBaltrusaitis/OpenFace/wiki/Unix-Installation)
3. Update the _\_setup_data.py_ file to point to your freshly build _FeatureExtraction_ executable (in the bin folder of openface).
4. Run _python openfaceInput.py_ . After a short duration (and _no_ errors) a new window should open, displaying your webcam image superimposed with makers of various sorts.
5. If there are any errors during the last call, try changing the _webcam_device_id_ in \_setup_data.py or try running the FeatureExtraction program by itself. (the python code also just runs it using _subprocess_). 
6. If you ran into any problems, contact Sören.

### Acquiring Data (_data_acquisiton_v1_)
This is a non-natural acqusition method, meaning you will not actually play piano, but rather only look at various things.
There are some hyper-parameters to the data:
1. Where the webcam is, split up in **above_screen** (meaning above the computer screen where webcams usually are) and **below_screen** (meaning put ontop whatever the monitor is standing on)
2. Whether or not you made an effort to be in the middle (center) of the webcam picture (when looking at the screen, both vertical and horizontally)

If you have the time to do multiple hyper-parameter variations, do them in the following priority:

(below, centered) -> (below, non-centered) -> (above, centered) -> (above, non-centered)

**Warning: you will be filmed!**
There are three types of data being captured: 1. the position of markers etc. from openface as csv data, 2. Image cutouts of your face for each frame (to supplement the csv data) and ~~3. a still image from the webcam to get a sense of the camera position / your face in the image~~ (work in progress).

**The image data is only for debugging purposes and you don't have to submit them if you don't want to! There is the option to only submit the csv data!** The image data is only to check why certain frames / data-sets might have poor classification results. **The image data will be encrypted.** The images will be encrypted using a symmetric key (freshly generated on your end) which will be encrypted using an public/private key method (RSA) and submitted with the data. They can only be decrypted by someone having the private key (Sören). If you have any questions/feedback regarding this, contact Sören and have a look at the crypto.py file.

If you understood all this you can go ahead and capture some data!

#### Actual Acquisition
1. Set yourself up according to the hyper-parameters you want to do in this run. Make sure the only face in the video is yours.
2. run _python data_acquisiton_v1.py_
3. the program will ask some questions (name, the hyperparameters mentioned above, and some questions regarding lighting etc.)
4. after answering all questions you are ready to go. The openface window should open; click back into the terminal so you can continue to interact with it
5. The process is the following. You are asked to look at a target (SCREEN, KEYBOARD, AIR). You start looking at it, press enter, continue to look at it (swaying your head left and right/up and down, basically doing a fast forward through all poses in which you could naturally look at the target) and then press enter again (without looking at the screen beforehand!, so best leave your finger on the enter key). Then you repeat the the process for the other targets. 'AIR' is supposed to describe the state where you neither look at something on the screen, nor on the keyboard.
7. If something goes wrong (e.g. you looked at the screen eventhough you were not supposed to) you can abort using ctrl-c and start over.
8. After you looked at all three targets, the program asks you if and what data you want to share (read: copy it into a folder which will be added by _git add ._)
9. After you are done with all the hyper-parameter runs you can either add all the new folders in _openface_data_ to the git (remember the images are encrypted) or send me the folders using a different method.

**Thanks!**


### old readme:

# Piano with Dexmo (2020)

This project is about guided learning of rhythm and timing.

A hand-exoskeleton and a keyboard (connected via MIDI) are used to record the user's musical performance as well as to give respective feedback to their fingers.


## Features
* Hier könnte Ihre Werbung stehen.


## Required software/packages
* Python 3.6
* python-rtmidi v1.4.1 (via PIP3, needs Debian/Ubuntu package *libjack-dev*)
* LilyPond [v2.18.2](http://lilypond.org/download/binaries/) (available in ubuntu bionic packages)
* python3-tk v3.6.9-1\~18.04 (available in ubuntu bionic packages)
* Qsynth v0.5.0-2 (available in ubuntu bionic packages) - e.g. if the keyboard does not have its own audio output
* vmpk v0.4.0-3 (available in ubuntu bionic packages) - virtual midi keyboard, if no physical one is available
* Debian/Ubuntu package *libasound-dev* might be required (if error "Cannot find alsa/asoundlib.h" occurs)

### requirements.txt
includes required python packages:
* pianoplayer v2.1.0
* MIDIUtil v1.2.1
* mido v1.2.9
* music21 v6.1.0

in order to install the packages run: 
```
$ pip3 install -r requirements.txt
```

## Prerequisites
* Properly connect Dexmo (Lego) and the keyboard/piano (the ports can be checked with the `aconnect` command)
* If used, Qsynth should be running beforehand


## Running the code
Starting the "main" program:
```
$ python3 dexmoPianoGui.py
```


## MIDI file generation
MIDI files are generated by the *generateMidi* function in [midiProcessing.py](https://github.com/abarch/comp_scaffold/blob/interactionLoop/DexmoPiano/midiProcessing.py).
The arguments are:

| Argument | Type | Explanation |
| ---: | :---: | :--- |
| noteValues | [float] | "Lengths" of the notes (e.g. 1, 1/2 etc.) |
| notesPerBar | [int] | Amounts of notes that a bar can contain |
| noOfBars | int | Number of bars (plus initial empty bar for metronome) |
| pitches | [int] | MIDI pitch numbers (0-127), see [here](https://newt.phys.unsw.edu.au/jw/notes.html) |
| bpm | int | Beats per minute |
| left | bool | *True*: generate notes for left hand |
| right | bool | *True*: generate notes for right hand |
| outfiles | [4× str] | Paths to output files: midi, midi+metronome, midi+metronome+dexmo, musicXML |

When running the program (GUI), most of these settings can be adjusted in the options window (click on *Specify next Task*)

To manually generate MIDI files, set the desired arguments at the bottom of the script and run
```
$ python3 midiGen.py
```





<!-- ## Authors
* **Janneke Simmering**
* **Jessica Seidel**
* **Tobias Coppenrath** -->


## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.


## Background
Group project for *Intelligent Systems*, organized by Alexandra Moringen and Guillaume Walck (Bielefeld University).
