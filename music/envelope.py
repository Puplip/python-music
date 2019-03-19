
from .wavetable import WaveTable

from typing import List

from .__init__ import sample_rate

import math





class Envelope():
    def apply(self, sound : List[float], **kargs):
        raise NotImplementedError
    
    @staticmethod
    def linear(x : float):
        """
        linear envelope
        """
        return x
    
    @staticmethod
    def quadratic_positive(x : float):
        """
        upwards facing parabola defined by: x^2
        """
        return x ** 2

    @staticmethod
    def quadratic_negative(x : float):
        """
        downward facing parabola defined by: 1 - (x - 1) ^ x
        """
        return 1.0 - (x - 1.0) ** 2
    
    @staticmethod
    def quarter_sin(x : float):
        """
        quarter sine wave (downwards curvature) defined by: sin(2*pi*x)
        """
        return math.sin(2*math.pi*x)
    
    @staticmethod
    def half_sin(x : float):
        """
        half sine wave defined by: (sin((x - 1/2) * pi) + 1)/2
        """
        return (math.sin(math.pi * (x - 1/2)) + 1) / 2
    
    @staticmethod
    def exponential(x : float, p : float = 50):
        """
        exponential envelope defined by: ((1/p)^(x) - 1) / (1/p - 1)
        (downwards curvature)
        """
        a = 1/p

        return ((a ** x) - 1) / (a - 1)
    
    @staticmethod
    def exponential_upfacing(x : float, p : float = 50):
        """
        exponential envelope defined by: ((p)^(x) - 1) / (p - 1)
        same as exponential, but with upwards curvature
        """
        a = 1/p

        return ((a ** x) - 1) / (a - 1)


class ADSR(Envelope):
    def __init__(self, attack : float, decay : float, sustain : float, release : float, **kargs):
        """
        Creates an ADSR Envelope with the specified parameters.

            attack: length of attack in ms
            decay:  length of the decay in ms
            sustain: level fo the sustain [0,1]
            release: length of the release in ms

        Optional Arguments:

            attack_function: function defining the shape of the attack
                default: Envelope.exponential
            decay_function: function defining the shape of the decay
                default: Envelope.exponential
            release_function: function defining the shape of the release
                default: Envelope.exponential
            
        Note: the decay and release functions are applied as: 1 - f(x)
        """

        if "attack_function" in kargs:
            self.attack_function = kargs.attack_function
        else:
            self.attack_function = Envelope.exponential
        
        if "decay_function" in kargs:
            self.decay_function = kargs.decay_function
        else:
            self.decay_function = Envelope.exponential
        
        if "release_function" in kargs:
            self.release_function = kargs.release_function
        else:
            self.release_function = Envelope.exponential

        self.attack_start = 0
        self.attack_length = attack
        self.attack_end = self.attack_start + self.attack_length

        self.decay_start = self.attack_end
        self.decay_length = decay
        self.decay_end = self.decay_start + self.decay_length

        self.sustain_level = sustain

        self.release_length = release

        # convert the timings to samples
        self.attack_start *= sample_rate / 1000
        self.attack_length *= sample_rate / 1000
        self.attack_end *= sample_rate / 1000

        self.decay_start *= sample_rate / 1000
        self.decay_length *= sample_rate / 1000
        self.decay_end *= sample_rate / 1000

        self.release_length *= sample_rate / 1000

    def apply(self, sound : List[float], **kargs):

        output = list()

        for i, sample in enumerate(sound):
            if i < self.attack_end:
                output.append(self.attack_function(i / self.attack_length) * sample)
            elif i < self.decay_end:
                output.append((1 - self.decay_function((i - self.decay_start) / self.decay_length) * (1 - self.sustain_level)) * sample)
            elif i >= (len(sound) - self.decay_length):
                output.append(self.sustain_level * (1 - self.release_function((i - len(sound) + self.release_length) / self.release_length)) * sample)
            else:
                output.append(self.sustain_level * sample)
    
    