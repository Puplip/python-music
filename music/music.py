

# from .envelope import 

from typing import List

from .parameters import sample_rate

from .utils import *

from mido import MidiFile

class Vibrato():
    none = 0
    full = 1
    linear = 2
    exp = 3

class Tempo():
    def __init__(self, bpm : float):
        self.bpm = bpm
        self.beat_samples = sample_rate / (bpm / 60.0 )
    def get_time(self, beat : float):
        return self.beat_samples * beat
    
class Note():

    def __init__(self, tempo : Tempo, beat : float, length : List[float], pitch : List[int], volume : float = 1.0, vibrato : int = Vibrato.none, vibrato_amplitude : float = 20.0):
        """
        Note Initializer

        Required Arguments:
            tempo: Tempo object the note belongs to
            beat: beat the note starts on
            length: list of note lengths (floats)
            pitch: list of midi note numbers (integers)
        
        Optional Arguments:
            volume: float to scale the sound by (default: 1.0)
            vibrato: specifies the type of vibrato (default: Vibrato.none)
                Vibrato.none: no vibrato
                Vibrato.full: vibrato through the entire note
                Vibrato.linear: linearly increasing vibrato
                Vibrato.exp: exponentially increasing vibrato
            vibrato_amplitude: positive float specifying the amplitude of the vibrato in cents (default 20)
        """

        self.tempo = tempo
        self.beat = beat
        self.length = length
        self.pitch = pitch
        self.vibrato = vibrato
        self.vibrato_amplitude = vibrato_amplitude
        self.volume = volume

class Track():
    def __init__(self, data = list()):
        self.data = data
    def add_sound(self, sound : List[float], pos : int):
        if pos + len(sound) > len(self.data):
            for i in range(pos + len(sound) - len(self.data)):
                self.data.append(0.0)
        for i, sample in enumerate(sound):
            self.data[pos + i] += sample

    @staticmethod
    def mix(tracks : list, volumes : List[float]):
        new_track_data = ZeroList([max([len(y.data) for y in tracks])])
        for track, volume in zip(tracks, volumes):
            for i, sample in enumerate(track.data):
                new_track_data[i] += sample * volume
        return Track(new_track_data)
    
    def normalize(self):
        max_amp = max(self.data)

        self.data = [x / max_amp for x in self.data]
