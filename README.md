# Music
GUI to help with learning music theory or chord identification

0.2.0 is a stable build with the following features:

- Chord Identification 
    - enter 3-5 notes that make up most common chords; identifies chord and which common scales it can be found in
    - e.g., type 'C E G' in Chord ID tab, and output will be 'C Major     Found in the following scales: C Major F Major A minor ... 

- Common Scale Reference
    - Select a root note, scale type, and which types of chords to display
    - Builds chord progressions with roman numeral analysis
        - e.g., select Root Note: 'C', select Scale Type: 'Ionian/Major', select Chord Type: 'Seventh' for the following output:
            - C D E F G A B C
          
            - I: C-E-G-B
            - ii: D-F-A-C
            - iii: E-G-B-D
            - IV: F-A-C-E
            - V: G-B-D-F
            - vi: A-C-E-G
            - viio: B-D-F-A
            
 - MIDI Input:
    - Plug in any MIDI instrument and use it in the Chord ID tab instead of typing with your keyboard.
    - Interprets chords on the fly; stops reading inputs after a 2 second delay, after which any new inputs will clear the entry field
        - This allows for several chords to be analyzed much more quickly and without the need to take the hands off of the instrument to click buttons
          

The programming is meant to be flexible enough to allow for future improvements (listed in the wiki under TODO). The least flexible code relates to chord identification.
Chords are not hard-coded but are instead calculated based on the intervals between notes.
This is done so that chords like inversions (where the actual root note is moved up an octave) or more complex chords can be calculated.
However, this method uses a MASSIVE dictionary that contains the labels for chord name, notation, and the data needed for interval calcuation.
This dictionary needs to be updated for all possible chords in western music, which goes against the idea that this program needs to be, first and foremost, scalable.
How can these instead be generated?

This highlights one of the purposes of developing this program in the first place: 
How deep does the musical rabbit hole go? 
How intricate are the relationships in music?
What is the simplest way to define these relationships?
