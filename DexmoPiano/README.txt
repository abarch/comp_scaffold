Manual for Piano with Dexmo first Demo:

- a synthesizer must be running (for example Qsynth, Fluidsynth)
  and MIDI through port must be connected with it (aconnect "port1" "port2")
  to get midi_interface_sound

- maybe you have to change the midi_interfaces in DexmoOutput.py
  and threadHandler.py (Piano Input)

- connect a Keyboard or start a virtual Keyboard (vmpk)  

- when LegoDexmo is plugged in, you can start DexmoPianoGui.py
