#ifndef MIDI_HAPTIC_DEFINITION_h
#define MIDI_HAPTIC_DEFINITION_h

// define the start of numberring of the channels
// user should define this
#ifndef MHP_CHAN_BASE
 #warning Base channel not selected, consider defining MHP_CHAN_BASE, using 10 now
  #define MHP_CHAN_BASE 10
#endif
// channel offsets added to the start of numberring
#define MHP_CHANOFFSET_RH 0
#define MHP_CHANOFFSET_LH 1
#define MHP_RH_CHAN MHP_CHAN_BASE + MHP_CHANOFFSET_RH
#define MHP_LH_CHAN MHP_CHAN_BASE + MHP_CHANOFFSET_LH

// note letter to offset from octave base
#define NOTE_C  0
#define NOTE_CS 1 // C-sharp  
#define NOTE_DF 1 // D-flat  
#define NOTE_D  2
#define NOTE_DS 3 // D-sharp  
#define NOTE_EF 3 // E-flat 
#define NOTE_E  4
#define NOTE_F 5 
#define NOTE_FS 6 
#define NOTE_GF 6 
#define NOTE_G 7
#define NOTE_GS 8 
#define NOTE_AF 8
#define NOTE_A 9
#define NOTE_AS 10
#define NOTE_BF 10
#define NOTE_B 11
 
// note base number for each octave
#define OCTAVE_m1  0
#define OCTAVE_0  12 
#define OCTAVE_1  24
#define OCTAVE_2  36
#define OCTAVE_3  48
#define OCTAVE_4  60  
#define OCTAVE_5  72  
#define OCTAVE_6  84  
#define OCTAVE_7  96  
#define OCTAVE_8  108  
#define OCTAVE_9  120 // not full up to G9 

// octave for each action for given finger name
#define MHP_ACT_THB OCTAVE_1
#define MHP_ACT_IND OCTAVE_2
#define MHP_ACT_MID OCTAVE_3
#define MHP_ACT_RNG OCTAVE_4
#define MHP_ACT_PKY OCTAVE_5

// octave for each action for given finger number
#define MHP_ACT_1 OCTAVE_1
#define MHP_ACT_2 OCTAVE_2
#define MHP_ACT_3 OCTAVE_3
#define MHP_ACT_4 OCTAVE_4
#define MHP_ACT_5 OCTAVE_5

// action mode FLX is Flex, EXT is Extension, IMP is Impulsion
#define MHP_ACT_FLX NOTE_F
#define MHP_ACT_EXT NOTE_E
#define MHP_ACT_IMP NOTE_A

// control number for each angle
#define MHP_STA_LSB_OFFSET  32
#define MHP_STA_THBR 20
#define MHP_STA_THBR2 MHP_STA_THBR + MHP_STA_LSB_OFFSET
#define MHP_STA_THBS 21
#define MHP_STA_THBS2 MHP_STA_THBS + MHP_STA_LSB_OFFSET
#define MHP_STA_THBB 22
#define MHP_STA_THBB2 MHP_STA_THBB + MHP_STA_LSB_OFFSET

#define MHP_STA_INDS 23
#define MHP_STA_INDS2 MHP_STA_INDS + MHP_STA_LSB_OFFSET
#define MHP_STA_INDB 24
#define MHP_STA_INDB2 MHP_STA_INDB + MHP_STA_LSB_OFFSET

#define MHP_STA_MIDS 25
#define MHP_STA_MIDS2 MHP_STA_MIDS + MHP_STA_LSB_OFFSET
#define MHP_STA_MIDB 26
#define MHP_STA_MIDB2 MHP_STA_MIDB + MHP_STA_LSB_OFFSET

#define MHP_STA_RNGS 27
#define MHP_STA_RNGS2 MHP_STA_RNGS + MHP_STA_LSB_OFFSET
#define MHP_STA_RNGB 28
#define MHP_STA_RNGB2 MHP_STA_RNGB + MHP_STA_LSB_OFFSET

#define MHP_STA_PKYS 29
#define MHP_STA_PKYS2 MHP_STA_PKYS + MHP_STA_LSB_OFFSET
#define MHP_STA_PKYB 30
#define MHP_STA_PKYB2 MHP_STA_PKYB + MHP_STA_LSB_OFFSET



#endif
