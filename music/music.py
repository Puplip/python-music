

# from .envelope import 

from typing import List

from .parameters import sample_rate

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

    def __init__(self, tempo : Tempo, beat : float, length : List[float], pitch : List[int], vibrato : int = Vibrato.none, vibrato_amplitude : float = 20.0):
        """
        Note Initializer

        Required Arguments:
            length: list of note lengths (floats)
            pitch: list of midi note numbers (integers)
        
        Optional Arguments:
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


