from __future__ import division
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import math
from pyaudio import PyAudio
import pygame
import pygame.midi
import time
import random

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range


## Init pygame and assign a device

pygame.midi.init()
print("\nInput Devices:")
dev_input_count = 0
for idx, device in enumerate(range(pygame.midi.get_count())):
    if pygame.midi.get_device_info(device)[2] == 1:
        print(str(idx + 1) + '.', pygame.midi.get_device_info(device)[1].decode('utf-8'))
        dev_input_count += 1
if dev_input_count == 0:
    print("None\n")
    print("No input device found. MIDI features will not be available.")
    print("Please connect a device and restart Music (with Sound) to regain MIDI features.")
else:
    device_num = int(input("\nPlease enter the number of your input device:\n")) - 1
    kb = pygame.midi.Input(device_num)

    
## Create Root Window

root = Tk()

    # Window Settings
root_geo = [345, 345]
root.title('Music (Without Sound)')
root.geometry(str(int(root_geo[0])) + 'x' + str(int(root_geo[1])))
root.resizable(1, 0)

## Create Sine Tone - Serious Issues with high volume 

def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(3), # 8bit
                    channels=2, # adjust for speed
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()


class Note:


    def __init__(self):
        self.old_time_val = 0
        self.all_notes_optionmenu = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#',
                          'A', 'A#', 'B', 'Random']
        self.oct_4_freqs = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23,
                           369.99, 392.00, 415.30, 440.00, 466.16, 493.88]
        self.scales_optionmenu = {'Major/Ionian': [2, 2, 1, 2, 2, 2, 1],
                       'Natural Minor/Aeolian': [2, 1, 2, 2, 1, 2, 2],
                       'Melodic Minor': [2, 1, 2, 2, 2, 2, 1],
                       'Harmonic Minor': [2, 1, 2, 2, 1, 3, 1],
                       'Dorian': [2, 1, 2, 2, 2, 1, 2],
                       'Phrygian': [1, 2, 2, 2, 1, 2, 2],
                       'Lydian': [2, 2, 2, 1, 2, 2, 1],
                       'Mixolydian': [2, 2, 1, 2, 2, 1, 2],
                       'Locrian': [1, 2, 2, 1, 2, 2, 2],
                                  'Random': []}
        self.intervals = ['Unison', 'Minor 2nd', 'Major 2nd',
                          'Minor 3rd', 'Major 3rd', 'Perfect 4th',
                          'Tritone', 'Perfect 5th', 'Minor 6th',
                          'Major 6th', 'Minor 7th', 'Major 7th',
                          'Octave']
        self.chord_patterns = {'Major': [['Major 3rd', 'Minor 3rd'],
                                         []],
                               'Major - 1st Inversion': [['Minor 3rd', 'Perfect 4th'],
                                         []],
                               'Major - 2nd Inversion': [['Perfect 4th', 'Major 3rd'],
                                         []],
                               'Minor': [['Minor 3rd', 'Major 3rd'],
                                         []],
                               'Minor - 1st Inversion': [['Major 3rd', 'Perfect 4th'],
                                         []],
                               'Minor - 2nd Inversion': [['Perfect 4th', 'Minor 3rd'],
                                         []],
                               'Diminished': [['Minor 3rd', 'Minor 3rd'],
                                              [f'\N{SUPERSCRIPT ZERO}']],
                               'Diminished - 1st Inversion': [['Minor 3rd', 'Tritone'],
                                              [f'\N{SUPERSCRIPT ZERO}']],
                               'Diminished - 2nd Inversion': [['Tritone', 'Minor 3rd'],
                                              [f'\N{SUPERSCRIPT ZERO}']],
                               'Augmented': [['Major 3rd', 'Major 3rd'],
                                             [f'\N{PLUS SIGN}']],
                               'Major Seventh': [['Major 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Major Seventh - 1st Inversion': [['Minor 3rd',
                                                                  'Major 3rd',
                                                                  'Minor 2nd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Major Seventh - 2nd Inversion': [['Major 3rd',
                                                                  'Minor 2nd',
                                                                  'Major 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Major Seventh - 3rd Inversion': [['Minor 2nd',
                                                                  'Major 3rd',
                                                                  'Minor 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Seventh': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd'],
                                                 [f'\N{DIGIT SEVEN}']],
                               'Minor Seventh - 1st Inversion': [['Major 3rd',
                                                                  'Minor 3rd',
                                                                  'Major 2nd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Seventh - 2nd Inversion': [['Minor 3rd',
                                                                  'Major 2nd',
                                                                  'Minor 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Seventh - 3rd Inversion': [['Major 2nd',
                                                                  'Minor 3rd',
                                                                  'Major 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Dominant Seventh': [['Major 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd'],
                                                    [f'\N{DIGIT SEVEN}']],
                               'Dominant Seventh - 1st Inversion': [['Minor 3rd',
                                                                  'Minor 3rd',
                                                                  'Major 2nd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Dominant Seventh - 2nd Inversion': [['Minor 3rd',
                                                                  'Major 2nd',
                                                                  'Major 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Dominant Seventh - 3rd Inversion': [['Major 2nd',
                                                                  'Major 3rd',
                                                                  'Minor 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Major Seventh': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Major 3rd'],
                                                       ['mM' + f'\N{DIGIT SEVEN}']],
                               'Minor Major Seventh - 1st Inversion': [['Major 3rd',
                                                                  'Major 3rd',
                                                                  'Minor 2nd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Major Seventh - 2nd Inversion': [['Major 3rd',
                                                                  'Minor 2nd',
                                                                  'Minor 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Minor Major Seventh - 3rd Inversion': [['Minor 2nd',
                                                                  'Minor 3rd',
                                                                  'Major 3rd'],
                                                 ['M' + f'\N{DIGIT SEVEN}']],
                               'Diminished Seventh': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd'],
                                                      [f'\N{SUPERSCRIPT ZERO}'\
                                                       + f'\N{DIGIT SEVEN}']],
                               'Half-Diminished Seventh': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + f'\N{DIGIT SEVEN}']],
                               'Half-Diminished Seventh - 1st Inversion': [['Minor 3rd',
                                                                            'Major 3rd',
                                                                            'Major 2nd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + f'\N{DIGIT SEVEN}']],
                               'Half-Diminished Seventh - 2nd Inversion': [['Major 3rd',
                                                                            'Major 2nd',
                                                                            'Minor 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + f'\N{DIGIT SEVEN}']],
                               'Half-Diminished Seventh - 3rd Inversion': [['Major 2nd',
                                                                            'Minor 3rd',
                                                                            'Minor 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + f'\N{DIGIT SEVEN}']],
                               'Augmented Major Seventh': [['Major 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd'],
                                                           [f'\N{PLUS SIGN}' +\
                                                            f'\N{DIGIT SEVEN}']],
                               'Augmented Major Seventh - 1st Inversion': [['Major 3rd',
                                                                            'Minor 3rd',
                                                                            'Minor 2nd'],
                                                           [f'\N{PLUS SIGN}' +\
                                                            f'\N{DIGIT SEVEN}']],
                               'Augmented Major Seventh - 2nd Inversion': [['Minor 3rd',
                                                                            'Minor 2nd',
                                                                            'Major 3rd'],
                                                           [f'\N{PLUS SIGN}' +\
                                                            f'\N{DIGIT SEVEN}']],
                               'Augmented Major Seventh - 3rd Inversion': [['Minor 2nd',
                                                                            'Major 3rd',
                                                                            'Major 3rd'],
                                                           [f'\N{PLUS SIGN}' +\
                                                            f'\N{DIGIT SEVEN}']],
                               'Add9': [['Major 3rd',
                                               'Minor 3rd',
                                               'Perfect 5th'],
                                               ['Add9']],
                               'mAdd9': [['Minor 3rd',
                                               'Major 3rd',
                                               'Perfect 5th'],
                                               ['mAdd9']],
                               'Add2': [['Major 2nd',
                                               'Major 2nd',
                                               'Minor 3rd'],
                                               ['Add2']],
                               'mAdd2': [['Major 2nd',
                                               'Minor 2nd',
                                               'Major 3rd'],
                                               ['mAdd2']],
                               'Major Ninth': [['Major 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                               'Minor 3rd'],
                                               [f'\N{LATIN CAPITAL LETTER M}'+\
                                                f'\N{DIGIT NINE}']],
                               'Minor Ninth': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd'],
                                               [f'\N{DIGIT NINE}']],
                               'Dominant Ninth': [['Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                               'Major 3rd'],
                                                  [f'\N{DIGIT NINE}']],
                               'Dominant Minor Ninth': [['Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd'],
                                                            ['7b9']],
                               'Major Seventh Sharp Ninth': [['Major 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                               'Perfect 4th'],
                                                             ['M7#9']],
                               'Minor Seventh Flat Ninth': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd'],
                                                             ['m7b9']],
                               'Minor Major Ninth': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Major 3rd',
                                                      'Minor 3rd'],
                                                       ['mM' + f'\N{DIGIT NINE}']],
                               'Augmented Major Ninth': [['Major 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd',
                                                          'Minor 3rd'],
                                                           [f'\N{PLUS SIGN}' +\
                                                            'M' +\
                                                            f'\N{DIGIT NINE}']],
                               'Augmented Dominant Ninth': [['Major 3rd',
                                                 'Major 3rd',
                                                 'Major 2nd',
                                                          'Major 3rd'],
                                                           ['9#5']],
                               'Major Sharp Ninth': [['Major 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Major 3rd'],
                                                           ['M' + f'\N{NUMBER SIGN}' +\
                                                            f'\N{DIGIT NINE}']],
                               'Diminished Ninth': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                      'Perfect 4th'],
                                                      [f'\N{SUPERSCRIPT ZERO}'\
                                                        + f'\N{DIGIT NINE}']],
                               'Diminished Minor Ninth': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                      'Major 3rd'],
                                                      [f'\N{SUPERSCRIPT ZERO}'\
                                                       + 'b' + f'\N{DIGIT NINE}']],
                               'Half-Diminished Ninth': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Major 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + f'\N{DIGIT NINE}']],
                               'Half-Diminished Minor Ninth': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Minor 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + 'b' + f'\N{DIGIT NINE}']],
                               'Major Eleventh': [['Major 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                                'Minor 3rd'],
                                               ['M11']],
                               'Dominant Eleventh': [['Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                                'Minor 3rd'],
                                                     ['11']],
                               'Minor Major Eleventh': [['Minor 3rd',
                                               'Major 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                                'Minor 3rd'],
                                               ['mM11']],
                               'Minor Eleventh': [['Minor 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                                'Minor 3rd'],
                                               ['m11']],
                               'Augmented Major Eleventh': [['Major 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                                'Major 3rd'],
                                               [f'\N{PLUS SIGN}' + 'M11']],
                               'Augmented Minor Eleventh': [['Major 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                                'Minor 3rd'],
                                               [f'\N{PLUS SIGN}' + 'm11']],
                               'Augmented Eleventh': [['Major 3rd',
                                               'Major 3rd',
                                               'Major 2nd',
                                               'Major 3rd',
                                                'Minor 3rd'],
                                               [f'\N{PLUS SIGN}' + '11']],
                               'Half-Diminished Eleventh': [['Minor 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                               'Major 3rd',
                                                'Minor 3rd'],
                                               [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + '11']],
                               'Diminished Eleventh': [['Minor 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                                'Perfect 4th'],
                                               [f'\N{SUPERSCRIPT ZERO}'\
                                                            + '11']],
                               'Minor Seventh Minor Ninth Minor Eleventh': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                'Major 3rd'],
                                                             ['7m9m11']],
                               'Major Eleventh Flat Ninth': [['Major 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                               'Minor 3rd',
                                                'Major 3rd'],
                                               [f'\N{LATIN CAPITAL LETTER M}' + '11b9']],
                               'Half-Diminished Minor Eleventh': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Minor 3rd',
                                                            'Major 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + 'b11']],
                               'Minor Sharp Eleventh': [['Minor 3rd',
                                                 'Major 3rd',
                                                 'Minor 3rd',
                                                          'Major 3rd',
                                                         'Major 3rd'],
                                                           ['m#11']],
                               'Dominant Eleventh Sharp Ninth': [['Major 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                          'Minor 3rd',
                                                         'Major 3rd'],
                                                           ['11#9']],
                               'Diminished Minor Eleventh': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                      'Major 3rd',
                                                              'Minor 3rd'],
                                                      [f'\N{SUPERSCRIPT ZERO}'\
                                                       + 'b11']],
                               'Major Sharp Eleventh': [['Major 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Major 3rd',
                                                         'Minor 3rd'],
                                                           ['M#11']],
                               'Diminished Minor Ninth': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Minor 3rd',
                                                      'Major 3rd'],
                                                      [f'\N{SUPERSCRIPT ZERO}'\
                                                       + 'b' + f'\N{DIGIT NINE}']],
                               'Dominant Sharp Eleventh': [['Major 3rd',
                                               'Minor 3rd',
                                               'Minor 3rd',
                                               'Major 3rd',
                                                'Major 3rd'],
                                               [f'\N{PLUS SIGN}' + 'M11']],
                               'Half-Diminished Minor Ninth Minor Eleventh': [['Minor 3rd',
                                                 'Minor 3rd',
                                                 'Major 3rd',
                                                          'Minor 3rd',
                                                            'Minor 3rd'],
                                                           [f'\N{LATIN CAPITAL LETTER O WITH STROKE}'\
                                                            + 'b9b11']]}
        self.chord_types = ['Triad', 'Seventh', 'Ninth', 'Eleventh', 'Thirteenth']
##        self.note_imgs = ['
        
    @staticmethod
    def int_to_roman(input_value):
        """ Convert an integer to Roman numeral """
        if not isinstance(input_value, type(1)):
            raise TypeError("expected integer, got %s" % type(input_value))
        if not 0 < input_value < 4000:
            raise ValueError("Argument must be between 1 and 3999")
        ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
        nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
        result = []
        for i in range(len(ints)):
            count = int(input_value / ints[i])
            result.append(nums[i] * count)
            input_value -= ints[i] * count
        return ''.join(result)
    
    @staticmethod
    def roman_to_int(input_value):
        """ Convert a Roman numeral to an integer. """
        if not isinstance(input_value, type("")):
            raise TypeError("expected string, got %s" % type(input_value))
        input_value = input_value.upper()
        nums = {'M':1000, 'D':500, 'C':100, 'L':50, 'X':10, 'V':5, 'I':1}
        sum = 0
        for i in range(len(input_value)):
            try:
                value = nums[input_value[i]]
                # If the next place holds a larger number, this value is negative
                if i+1 < len(input_value) and nums[input_value[i+1]] > value:
                    sum -= value
                else: sum += value
            except KeyError:
                raise ValueError('input is not a valid Roman numeral: %s' % input_value)
        # easiest test for validity...
        if int_to_roman(sum) == input_value:
            return sum
        else:
            raise ValueError('input is not a valid Roman numeral: %s' % input_value)

    @staticmethod
    def toggle(toggle_btn):
        ''' Set the relief property of a button to emulate it being toggled '''
        if toggle_btn.config('relief')[-1] == SUNKEN:
            toggle_btn.config(relief=RAISED)
        else:
            toggle_btn.config(relief=SUNKEN)
        
    def get_note_freq(self, note = 'C'):
        """ Return the frequency of a note. """
        for idx, ind_note in enumerate(self.all_notes_optionmenu):
            if note == ind_note:
                return idx, self.oct_4_freqs[idx]

    def transpose_pattern(self, root_note, pattern):
        """ Return a list of indices, notes, and frequencies. """
        octave_chg = 0
        idx = self.get_note_freq(note = str(root_note))[0]
        transpos_freqs = [self.oct_4_freqs[idx]]
        transpos_idxs = [idx]
        transpos_idx = idx
        transpos_notes = []
        for step in pattern:
            transpos_idx = transpos_idx + step
            transpos_idxs.append(transpos_idx)
            if (transpos_idx > 23):
                octave_chg = 2
            elif (transpos_idx > 11):
                octave_chg = 1
            elif (transpos_idx < -12):
                octave_chg = 2
            elif (transpos_idx < 0):
                octave_chg = 1
            try:
                transpos_freq = (self.oct_4_freqs[transpos_idx])*(2**octave_chg)
                transpos_freqs.append(transpos_freq)
            except IndexError as e:
                transpos_freq = (self.oct_4_freqs[(transpos_idx) % 12])*(2**octave_chg)
                transpos_freqs.append(transpos_freq)
        for i in transpos_idxs:
            transpos_notes.append(self.all_notes_optionmenu[i % 12])
        return transpos_idxs, transpos_notes, transpos_freqs
        
    def play_scale(self, scale_prog, freq_idx):
        """ Play the audio, note by note, of a scale. """
        i = 0
        for note in scale_prog:
            sine_tone(frequency=self.note_freqs[freq_idx[i]]/2, #must be divided by number of channels to maintain correct tone
                      duration=int(1), #somehow regulated by adjusting number of channels and correcting freq
                      volume=.01,
                      sample_rate=22050)
            i += 1

    def create_scale(self, root_note, scale_type):
        """ Return the notes and frequencies used in common scales. """
        if root_note == 'Random':
            root_note = random.choice(self.all_notes_optionmenu[0:-1])
        if scale_type == 'Random':
            scales = [k for k in self.scales_optionmenu.keys() if k != 'Random']
            scale_type = random.choice(scales)
        for k in self.scales_optionmenu:
            if k == scale_type:
                pattern = self.scales_optionmenu[k]
        idxs, notes, freqs = self.transpose_pattern(root_note, pattern)
        return notes, freqs

    def get_interval(self, root_note, final_note):
        """ Return the interval between two notes as a string. """
        note_1_idx = int()
        note_2_idx = int()
        for idx, note in enumerate(self.all_notes_optionmenu):
            if note == root_note:
                note_1_idx = idx
            if note == final_note:
                note_2_idx = idx
##        print(self.intervals[((note_2_idx) - (note_1_idx + 12)) % 12])
        return self.intervals[((note_2_idx) - (note_1_idx + 12)) % 12]

    def get_scale_chords(self, notes, chord_type):
        """ Return the chords within a scale and their Roman numerals. """
        i = 1
        j = 0
        rom_nums = []
        chords = []
        rom_num_chords = []
        if chord_type == 'Triad':
            for n in range(len(notes) - 1):
                chord = [notes[j%(len(notes)-1)], notes[(j+2)%(len(notes)-1)], notes[(j+4)%(len(notes)-1)]]
                chords.append(chord)
                j += 1
        elif chord_type == 'Seventh':
            for n in range(len(notes) - 1):
                chord = [notes[j%(len(notes)-1)], notes[(j+2)%(len(notes)-1)],
                         notes[(j+4)%(len(notes)-1)], notes[(j+6)%(len(notes)-1)]]
                chords.append(chord)
                j += 1
        elif chord_type == 'Ninth':
            for n in range(len(notes) - 1):
                chord = [notes[j%(len(notes)-1)], notes[(j+2)%(len(notes)-1)],
                         notes[(j+4)%(len(notes)-1)], notes[(j+6)%(len(notes)-1)],
                         notes[(j+8)%(len(notes)-1)]]
                chords.append(chord)
                j += 1
        elif chord_type == 'Eleventh':
            for n in range(len(notes) - 1):
                chord = [notes[j%(len(notes)-1)], notes[(j+2)%(len(notes)-1)],
                         notes[(j+4)%(len(notes)-1)], notes[(j+6)%(len(notes)-1)],
                         notes[(j+8)%(len(notes)-1)], notes[(j+10)%(len(notes)-1)]]
                chords.append(chord)
                j += 1
        elif chord_type == 'Eleventh':
            for n in range(len(notes) - 1):
                chord = [notes[j%(len(notes)-1)], notes[(j+2)%(len(notes)-1)],
                         notes[(j+4)%(len(notes)-1)], notes[(j+6)%(len(notes)-1)],
                         notes[(j+8)%(len(notes)-1)], notes[(j+10)%(len(notes)-1)],
                         notes[(j+12)%(len(notes)-1)]]
                chords.append(chord)
                j += 1
        for chord in chords:
            det_chord = self.determine_chord(chord)
            triad_notes = [chord[0], chord[1], chord[2]]
            triad = self.determine_chord(triad_notes)
            rom_num = self.int_to_roman(i)
            if (triad == 'Major') or (triad == 'Augmented'):
                rom_num = rom_num.upper()
            elif (triad == 'Minor') or (triad == 'Diminished'):
                rom_num = rom_num.lower()
            for k, v in self.chord_patterns.items():
                if k == det_chord:
                    rom_nums.append(rom_num + str(*v[1]))
            i += 1
        for idx, chord in enumerate(chords):
            note_string = '-'.join(chord)
##            print(rom_num_chords)
            rom_num_chords.append(str(rom_nums[idx]) + ': ' + note_string)
        return rom_num_chords

    def determine_chord(self, notes):
        """ Return the type of chord made by a series of notes. """
        chord_ints = []
        i = 0
        while i < len(notes) - 1:
            interval = self.get_interval(notes[i], notes[i + 1])
            chord_ints.append(interval)
            i += 1
        for k, v in self.chord_patterns.items():
            if v[0] == chord_ints:
                return k
            
    def create_scale_btn(self):
        text_area.delete('1.0', END)
        n = note_default.get()
        s1 = scale_default.get()
        c = chord_default.get()
        prog, freqs = self.create_scale(n, scale_type = s1)
        text_area.insert('1.0', prog)
        chord_area.delete('1.0', END)
        chords = self.get_scale_chords(prog, c)
        for idx, chord in enumerate(chords):
            chord_area.insert(END, chord)
            chord_area.insert(END, '\n')

    def create_SR_btn(self):
        note_SR_area.delete('1.0', END)
        n = note_default_optionmenu.get()
        s1 = scale_default_optionmenu.get()
        prog = self.create_scale(n, scale_type = s1)[0]
##        for idx, note in enumerate(prog):
##            img = self.note_imgs[idx]
        self.img = ImageTk.PhotoImage(Image.open(r"C:\Users\jusla\Pictures\small_test.png"))
##        note_SR_area.image_create(END, image = img)
        note_SR_area.create_image((10, 10), anchor = NW, image = self.img)

    def chordID_btn(self):
        note_CID_area.delete('1.0', END)
        notes = note_CID_input.get().strip().upper()
        notes = notes.split(" ")
        try:
            scales = []
            scale_types = []
            chord = self.determine_chord(notes)
            if "Inversion" not in chord:
                chord_id = str(notes[0] + " ") + chord
            else:
                if "1st" in chord:
                    chord_id = str(notes[-1] + " ") + chord
                elif "2nd" in chord:
                    chord_id = str(notes[-2] + " ") + chord
                elif "3rd" in chord:
                    chord_id = str(notes[-3] + " ") + chord
            note_CID_area.insert(END, chord_id)
        except:
            pass
        comp_notes = "-".join(notes)
        comp_dict = {}
        for note in self.all_notes_optionmenu:
            if note != 'Random':                
                for scale_type in self.scales_optionmenu:
                    if scale_type != 'Random':
                        prog, freqs = self.create_scale(note, scale_type)
                        for chord_type in self.chord_types:
                            compare_scale_chords = self.get_scale_chords(prog, chord_type)
                            for idx, i in enumerate(compare_scale_chords):
                                if comp_notes in i.split(" ")[1]:
                                    val = note + '-' + scale_type
                                    comp_dict[val] = 0
        if len(comp_dict.keys()) > 0:
            note_CID_area.insert(END, "\n\nFound in the following scales:\n")
            for k in comp_dict.keys():
                note_CID_area.insert(END, (k))
                note_CID_area.insert(END, "\n")
        
    def capture_midi(self):
        if kb.poll():
            time.sleep(.01)                
            midi_values = kb.read(1000)
            for value in midi_values:
                print("Value:", value)
                if value[0][0] == 144:
                    status = 'Engaged'
                elif value[0][0] == 128:
                    status = 'Released'
                else:
                    status = "Assign value for %d" % value[0][0]
                midi = value[0][1]
                time_val = value[1]
                modded_note_idx = midi % 12
                for idx, note_name in enumerate(self.all_notes_optionmenu):
                    if idx == modded_note_idx:
                        if tabControl.index("current") == 2\
                           and MIDI_input_toggle.config('relief')[-1] == SUNKEN\
                           and status == 'Engaged':
                            if self.old_time_val == 0:
                                self.old_time_val = time_val
                            if time_val - self.old_time_val < 2000:
                                note_CID_input.insert(END, self.all_notes_optionmenu[idx] + " ")
                            else:
                                note_CID_input.delete(0, END)
                                note_CID_input.insert(END, self.all_notes_optionmenu[idx] + " ")
                                print(time_val, self.old_time_val)
                        print(self.all_notes_optionmenu[idx])
                self.old_time_val = time_val
                self.chordID_btn()
                print(midi, status)
        root.after(10, self.capture_midi)
    
        
## Create Variables for Widgets

note = Note()
note_default = StringVar()
note_default.set(note.all_notes_optionmenu[0])
scale_default = StringVar()
scale_default.set('Major/Ionian')
chord_default = StringVar()
chord_default.set(note.chord_types[1])
note_default_optionmenu = StringVar()
note_default_optionmenu.set(note.all_notes_optionmenu[0])
scale_default_optionmenu = StringVar()
scale_default_optionmenu.set('Major/Ionian')

## Add tabs to the Root Window

    # Create a Notebook for controlling tabs and add to frame 
tabControl = ttk.Notebook(root)
scaleTab = Frame(tabControl)
sightreadTab = Frame(tabControl)
cidTab = Frame(tabControl)

    # Add tabs to the tab controller
tabControl.add(scaleTab, text = 'Scales')
tabControl.add(sightreadTab, text = 'Sight Read')
tabControl.add(cidTab, text = 'Chord ID')

    # Pack tab controller to make tabs visible
tabControl.grid(row = 0, sticky = (W, E))

## Add Header

header_lbl = Label(scaleTab,
                   text = 'Create a Scale',
                   bg = '#ffe').grid(row = 1, sticky = 'nw', columnspan = 1)

## Add widgets to the Scale Frame

    # Note Progression
text_area = Text(scaleTab,
                 height = 2,
                 width = 40,
                 bg = 'white')
text_area.grid(row = 7, column = 0, columnspan = 2, sticky = 'sw')
scale_lbl = Label(scaleTab,
                  text = 'Note Progression',
                  bg = '#ffe'
                  ).grid(row = 6, column = 0, sticky = 'sw')

    # Chord Progression
chord_area = Text(scaleTab,
                  height = 8,
                  width = 40,
                  bg = 'white')
chord_area.grid(row = 9, column = 0, columnspan = 2, sticky = 's')
scale_lbl_chord = Label(scaleTab,
                        text = 'Chord Progression',
                        bg = '#ffe'
                        ).grid(row = 8, column = 0, sticky = 'sw')
chord_type_lbl = Label(scaleTab,
                       text = 'Chord Type:',
                       ).grid(row = 4, column = 0, sticky = (W, E))
chord_type_input =  OptionMenu(scaleTab,
                               chord_default,
                               *note.chord_types)
chord_type_input.grid(row = 5, column = 0, columnspan = 1, sticky = (W, E))

    # Create Note Selection Widgets
note_input_lbl = Label(scaleTab,
                       text = 'Root Note:'
                       ).grid(row = 2, column = 0, sticky = (W, E))
note_input = OptionMenu(scaleTab,
                        note_default,
                        *note.all_notes_optionmenu)
note_input.grid(row = 3, column = 0, columnspan = 1, sticky = (W, E))

    # Create Scale Type Widgets
scale_type_input_label = Label(scaleTab,
                               text = 'Scale Type:'
                               ).grid(row = 2, column = 1,
                                      columnspan = 1, sticky = (W, E))
scale_type_input = OptionMenu(scaleTab,
                              scale_default, # Sets the default option
                              *note.scales_optionmenu.keys()) # Sets list to use
scale_type_input.grid(row = 3, column = 1, sticky = (W, E))

    # Button for Create Scale
create_scale_btn = Button(scaleTab,
                          text = 'Create Scale',
                          command = lambda: note.create_scale_btn() 
                          ).grid(row = 5, column = 1,
                                 columnspan = 1, sticky = (SW, NE))

## Add widgets to the Sight Reading Frame

    # Header and Display Area
header_SR_lbl = Label(sightreadTab,
                      text = 'Practice Sight Reading',
                      bg = '#ffe').grid(row = 1, sticky = 'nw', columnspan = 1)
note_SR_area = Canvas(sightreadTab,
                      height = int(root_geo[1] - 5),
                      width = int(root_geo[0] - 5))
note_SR_area.grid(row = 5, column = 0,
                  columnspan = 2, rowspan = 3, sticky = 'sw')

    # Widgets for Scale Selection
note_SR_input_lbl = Label(sightreadTab,
                          text = 'Root Note:'
                          ).grid(row = 2, column = 0, sticky = (W, E))
note_SR_input = OptionMenu(sightreadTab,
                           note_default_optionmenu,
                           *note.all_notes_optionmenu)
note_SR_input.grid(row = 3, column = 0, columnspan = 1, sticky = (W, E))

    # Create Scale Type Widgets
scale_type_SR_label = Label(sightreadTab,
                            text = 'Scale Type:'
                            ).grid(row = 2, column = 1,
                                   columnspan = 1, sticky = (W, E))
scale_type_SR_input = OptionMenu(sightreadTab,
                                 scale_default_optionmenu, # Sets the default option
                                 *note.scales_optionmenu.keys()) # Sets list to use
scale_type_SR_input.grid(row = 3, column = 1, sticky = (W, E))
create_SR_btn = Button(sightreadTab,
                       text = 'Practice',
                       command = lambda: note.create_SR_btn()
                       ).grid(row = 4, column = 0,
                              columnspan = 2, sticky = (SW, NE))

## Add widgets to the Chord ID Frame

    # Header and Display Area
header_CID_lbl = Label(cidTab,
                       text = 'Chord Identification',
                       bg = '#ffe').grid(row = 1, sticky = 'nw', columnspan = 1)
note_CID_area = Text(cidTab,
                     height = 7,
                     width = 40,
                     bg = 'white')
note_CID_area.grid(row = 5, column = 0, columnspan = 2, sticky = 'sw')

    # Widgets for Chord Note Entry
note_CID_input_lbl = Label(cidTab,
                           text = 'Chord Notes*'
                           ).grid(row = 2, column = 0, sticky = (W, E))
note_CID_warning_lbl = Label(cidTab,
                             text = '*Must be entered as played on piano,',
                             bg = '#ffe'
                           ).grid(row = 1, column = 1, sticky = (W, E))
note_CID_warning2_lbl = Label(cidTab,
                             text = '(from left to right, sequentially,',
                             bg = '#ffe'
                           ).grid(row = 2, column = 1, sticky = (W, E))
note_CID_warning3_lbl = Label(cidTab,
                              text = 'and must be separated by spaces',
                              bg = '#ffe'
                           ).grid(row = 3, column = 1, sticky = (W, E))
note_CID_input = Entry(cidTab)
note_CID_input.grid(row = 3, column = 0, sticky = (W, E))
create_CID_btn = Button(cidTab,
                        text = 'ID Chord',
                        command = lambda: note.chordID_btn()
                        ).grid(row = 4, column = 0, sticky = (SW, NE))
MIDI_input_toggle = Button(cidTab,
                           text = 'MIDI Input',
                           relief = RAISED,
                           command = lambda: note.toggle(MIDI_input_toggle))
MIDI_input_toggle.grid(row = 4, column = 1, sticky = (NE))

if dev_input_count != 0:
    note.capture_midi()
if __name__ == '__main__':
    root.mainloop()
