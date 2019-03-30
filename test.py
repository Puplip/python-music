import music

import sys

import numpy as np

class Blips(music.Instrument):
    def __init__(self):
        self.wave_table = music.WaveTableHarmonic([1 / (n ** 2) for n in range(1,10)])
        self.envelope = music.ADSR(25,25,0.8,5)

class Bass(music.Instrument):
    def __init__(self):
        self.wave_table = music.WaveTableHarmonic([1 / (n) for n in range(1,100)])
        self.envelope = music.ADSR(20,20,0.8,25)

class Square(music.Instrument):
    def __init__(self):
        self.wave_table = music.square
        self.envelope = music.ADSR(20,20,0.8,25)

class Saw(music.Instrument):
    def __init__(self):
        self.wave_table = music.saw
        self.envelope = music.ADSR(20,20,0.8,25)

class OceanSaw(music.Instrument):
    def __init__(self):
        self.wave_table = music.ocean_saw
        self.envelope = music.ADSR(20,20,0.8,25)

if __name__ == "__main__":
    music.Midi(sys.argv[1]).synth(sys.argv[2],[Saw(),OceanSaw(),Saw(),Saw(),OceanSaw()])
