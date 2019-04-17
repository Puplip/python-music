
# from .wavetable import WaveTable

from typing import List

from .parameters import sample_rate

import math

from .utils import *


class EnvelopePoint():
    """
    Creates a point for specifying a point on the envelope and the region following it

        value: the amplitude of the envelope at the beginning of the region
            (most envelopes should start at 0)

        length: the length of the region (units depend of the length_type)

        length_type: string the type of length (default ratio)
            absolute: ms for time envelopes or hertz for frequency envelopes
            ratio: ratio [0 to 1] of the region following the point

            When both absolute and ratio types points are added to an envelope,
                all ratios will be applied to the length not taken by the absolute envelopes

    """
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
        (approaches slower first)
        """
        return x ** 2

    @staticmethod
    def quadratic_negative(x : float):
        """
        downward facing parabola defined by: 1 - (x - 1) ^ x
        (approaches faster first)
        """
        return 1.0 - (x - 1.0) ** 2
    
    @staticmethod
    def quarter_sin(x : float):
        """
        quarter sine wave (downwards curvature) defined by: sin(2*pi*x)
        (faster first)
        """
        return math.sin(2*math.pi*x)
    
    @staticmethod
    def half_sin(x : float):
        """
        half sine wave defined by: (sin((x - 1/2) * pi) + 1)/2
        (slower first)
        """
        return (math.sin(math.pi * (x - 1/2)) + 1) / 2
    
    @staticmethod
    def exponential(x : float, p : float = 50):
        """
        exponential envelope defined by: ((1/p)^(x) - 1) / (1/p - 1)
        (faster first)
        use a lambda function to change p
        """

        a = 1/p

        return ((a ** x) - 1) / (a - 1)
    
    @staticmethod
    def exponential_upfacing(x : float, p : float = 50):
        """
        exponential envelope defined by: ((p)^(x) - 1) / (p - 1)
        (slower first)
        use a lambda function to change p
        """
        a = 1/p

        return ((a ** x) - 1) / (a - 1)

    def __init__(self, value : float, length : float, length_type : str = "ratio", function = False):
        self.value = value
        self.length = length
        self.length_type = length_type
        if function:
            self.function = function
        else:
            self.function = EnvelopePoint.exponential


class Envelope():

    def __init__(self, points : List[EnvelopePoint]):

        self.points = list(points)

        self.ratio_points = set()
        self.absolute_points = set()

        self.absolute_length = 0
        self.ratio_length = 0

        self.cached_time_points = CacheDict(50)

        for point in self.points:
            if point.length_type == "ratio":
                self.ratio_points.add(point)
                self.ratio_length += point.length
            elif point.length_type == "absolute":
                self.absolute_points.add(point)
                self.absolute_length += point.length
            else:
                raise Exception(f"Invalid EnvelopePoint.length_type: '{point.length_type}'")
        

    def value(self, x, length = 1.0):

        if self.absolute_length > length:
            raise Exception(f"length: {length} is less that envelope's absolute length: {self.absolute_length}")
        
        if length not in self.cached_time_points:
        
            ratio_length = length - self.absolute_length

            point_times = list()

            pos = 0
            time = 0

            for point in self.points:
                
                if point.length_type == "ratio":
                    time = ratio_length * (point.length / self.ratio_length)
                elif point.length_type == "absolute":
                    time = point.length
                else:
                    raise Exception(f"Invalid EnvelopePoint.length_type: '{point.length_type}'")
                
                point_times.append((pos, time))
                pos += time
            
            self.cached_time_points[length] = point_times
        
        prev_start = False
        prev_point = False
        prev_length = False

        next_point = False

        # print(len(self.cached_time_points[length]), len(self.points))


        for (start, length), point in zip(self.cached_time_points[length], self.points):
            # print(start, length, point)
            if start <= x:
                prev_start = start
                prev_point = point
                prev_length = length
            else:
                next_point = point
                break

        delta_value = next_point.value - prev_point.value

        return  delta_value * prev_point.function((x - prev_start) / prev_length) + prev_point.value
    
    def apply(self, array : List[float]):
        output = list()

        for i, x in enumerate(array):
            output.append(x * self.value(i, len(array)))
        
        return output

class ADSR(Envelope):
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
    def __init__(self, attack : float, decay : float, sustain : float, release : float, **kargs):
        

        if "attack_function" in kargs:
            self.attack_function = kargs["attack_function"]
        else:
            self.attack_function = EnvelopePoint.exponential
        
        if "decay_function" in kargs:
            self.decay_function = kargs["decay_function"]
        else:
            self.decay_function = EnvelopePoint.exponential
        
        if "release_function" in kargs:
            self.release_function = kargs["release_function"]
        else:
            self.release_function = EnvelopePoint.exponential

        
        self.attack = EnvelopePoint(0,attack / 1000 * sample_rate,"absolute", self.attack_function)
        self.decay = EnvelopePoint(1,decay / 1000 * sample_rate,"absolute", self.decay_function)
        self.sustain = EnvelopePoint(sustain,1.0,"ratio", EnvelopePoint.linear)
        self.release = EnvelopePoint(sustain,release / 1000 * sample_rate,"absolute", self.release_function)
        self.end = EnvelopePoint(0,0)

        super().__init__([self.attack, self.decay, self.sustain, self.release, self.end])


    
    