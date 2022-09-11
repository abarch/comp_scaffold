# README
## 1. How to get started

### 1.1. Required software/packages
1. setup an environment with Python 3.9.5  
2. install  [libjack-dev](https://packages.debian.org/de/sid/libjack-dev)  
	```bash
	sudo apt-get install -y libjack-dev
	```
3. install [LilyPond](https://lilypond.org/index.en.html) (available in ubuntu bionic packages)
	```bash
	sudo apt-get install lilypond
	```
4. if the keyboard does not have its own audio output install [Qsynth](https://qsynth.sourceforge.io/qsynth-index.html#Intro) (available in ubuntu bionic packages)
	```bash
	sudo apt-get install -y qsynth
	```
5. if you dont have a physical keyboard you can install a virtuall keybord e.g. [vmpk](https://vmpk.sourceforge.io/) (available in ubuntu bionic packages)
	```bash
	sudo apt-get install vmpk
	```
6. Debian/Ubuntu package [libasound-dev](https://packages.debian.org/de/sid/libasound-dev) might be required (if error "Cannot find alsa/asoundlib.h" occurs)
	```bash
	sudo apt-get install -y libasound2-dev
	```

### 1.2. Install requirements
The requirements can be installed under  _comp_scaffold/DexmoPiano/requirements.txt_ via
```bash
pip install -r requirements.txt
```

## 2. Usage of the Program

### 2.1. Prerequisites
- Properly connect keyboard/piano (the ports can be checked with the `aconnect` command)  
- If used, Qsynth should be running beforehand

### 2.2. Running the code
Starting the "main" program:  
``` bash
python DexmoPiano/gp_training_gui.py  
```

### 2.3. GUI interaction
The interface is split into two states. The main state  and the practice mode state.

After selecting which ports are used for piano input and sound output the user can optionally enter his name so that data points can be attributed to him. Then the user can select the midi file of a music piece he wants to practice and is forwarded to the main state.

In the main state the user is only presented with the possibilities to play the piece, select a new song or play a demo of the piece. When clicking on the "Play Piece" button a metronome signals the playback speed starting with one empty bar. When finished the user is presented with the error measurements and the recommended practice mode is shown at the top center of the window. By selecting "Start Practice" the user can enter the presented practice mode and is forwarded to the practice mode state.

There are currently two practice modes implemented. One of them is the pitch practice mode. Here the user is not guided by a metronome and prompted to play note after note while focusing to hit the correct pitches while disregarding the timing. The other one is the timing practice mode. Here the user is guided by the metronome but all notes are mapped to the same key on the piano. 

After playing in the practice mode the user can either choose to return to the main state or practice again in the practice mode. Currently practice is automatically ended for timing practice mode after two iterations.

### 2.4. Data collection
While running the program data points are added in the main state by comparing the error created by playing in the main state before and after practicing in the practice mode. 
#### Data format
Datapoints are saved in an _*.h5_ format. 
Fields of the file are:
- midi_filename
- username
- practice_mode
- bpm
- error_before_left_timing
- error_before_right_timing
- error_before_left_pitch
- error_before_right_pitch
- error_after_left_timing
- error_after_right_timing
- error_after_left_pitch
- error_after_right_pitch

## 3. Evaluation of the data
The Gaussian process is implemented under _[comp_scaffold/DexmoPiano/task_generation/gaussian_process.py](./task_generation/gaussian_process.py)_
To evaluate the collected data received from the gaussian process, all collected _\*.h5_ files need to be  put under _comp_scaffold/DexmoPiano/practice_data_. Then the jupyter notebook _[comp_scaffold/DexmoPiano/gaussian_process_evaluation.ipynb](gaussian_process_evaluation.ipynb)_ can be started. 
The utility measure can be changed under section 3.

## License  
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](../LICENSE) file for details.

