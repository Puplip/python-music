
import typing
import math
import random

from .parameters import sample_rate

from .envelope import Envelope

from .utils import *


class WaveTable():
    """
    General class for storing one period of a wave
    """
    def __init__(self, function_continuous : typing.Callable[[float] , float], period : float, samples : int = 4096):
        """
        function_continuous: function to be sampled. eg. math.cos
        period: period of the function
        samples: the number of samples to retrieve from the function
        """
        self.wave_table = [function_continuous(x * period / samples) for x in range(samples)]
        self.samples = samples
        self.last_sample_index = 0

    def __get_sample_interp(self, sample : float):
        """
        Function used linearly interpolate between samples.
        returns linear interpolated value of self.wave_table[sample % self.samples]
        """

        # print(sample)
        return (self.wave_table[math.floor(sample) % self.samples] + self.wave_table[math.ceil(sample) % self.samples]) / 2.0

    def get_samples(self, frequency : float, **kwargs):
        """
        Function used for sampling the wave table to get an output at a set frequency.

        Required arguments:
            frequency: the frequency in hertz of the output

            One length specifier from:
                samples: the length in samples of the output
                length: the length in seconds of the output
                periods: the length in periods at frequency
        Optional arguments:
            starting_phase: phase to start the output at in radians
                default: 0
            random_phase: boolean indicating if a random phase offset should be applied
                default: False
        """

        samples = False

        if "samples" in kwargs:
            samples = kwargs["samples"]
        elif "length" in kwargs:
            length = kwargs["length"]
            samples = sample_rate * length
        elif "periods" in kwargs:
            periods = kwargs["periods"]
            samples = periods / frequency / sample_rate
        else:
            raise Exception("One of (samples, length, periods) must be specified.")
        
        samples = int(samples)

        start_sample = self.last_sample_index
        if "starting_phase" in kwargs:
            starting_phase = kwargs["starting_phase"]
            start_sample = starting_phase / math.pi * self.samples
        elif "random_phase" in kwargs:
            starting_phase = random.random() * math.pi
            start_sample = starting_phase / math.pi * self.samples
        
        table_step_size = self.samples * (frequency / sample_rate)
        output = list()

        sample = start_sample
        for i in range(samples):
            output.append(self.__get_sample_interp(sample))
            sample += table_step_size
        self.last_sample_index = sample
        return output

    def get_samples_bend(self, frequency1 : float, frequency2 : float, **kwargs):
        """
        Function used for sampling the wave table to get an output at a set frequency.

        Required arguments:
            frequency1: the frequency in hertz of the beginning of the ouput
            frequency2: the frequency in hertz of the end of the output

            One length specifier from:
                samples: the length in samples of the output
                length: the length in seconds of the output
        Optional arguments:
            starting_phase: phase to start the output at in radians
                default: 0
            random_phase: boolean indicating if a random phase offset should be applied
                default: False
        """

        samples = False

        if "samples" in kwargs:
            samples = kwargs["samples"]
        elif "length" in kwargs:
            length = kwargs["length"]
            samples = sample_rate * length
        else:
            raise Exception("One of (samples, length, periods) must be specified.")
        
        samples = int(samples)

        start_sample = self.last_sample_index
        if "starting_phase" in kwargs:
            starting_phase = kwargs["starting_phase"]
            start_sample = starting_phase / math.pi * self.samples
        elif "random_phase" in kwargs:
            starting_phase = random.random() * math.pi
            start_sample = starting_phase / math.pi * self.samples
        
        table_step_size = self.samples * (frequency1 / sample_rate)
        table_step_size_step_size = (self.samples * (frequency2 / sample_rate) - table_step_size) / samples
        output = list()

        sample = start_sample
        for i in range(samples):
            output.append(self.__get_sample_interp(sample))
            sample += table_step_size
            table_step_size += table_step_size_step_size
        self.last_sample_index = sample
        return output

class WaveTableHarmonic(WaveTable):
    """
    class for WaveTables represented by n-integer harmonics of the fundamental
        amplitudes: a list of floats representing the amplitude of each harmonic

        optional:
            phases: a list of the starting phases of each harmonic.
                default: [0 for x in range(len(amplitudes))]
            random-phases: indicates whether all harmonics should have a random phase
                default: false
            samples: number of samples to store in the table
                default: 4096
    """

    def __init__(self, amplitudes : typing.List[float], **kargs):
        
        self.last_sample_index = 0

        phases = False
        if "phases" in kargs:
            phases  = kargs["phases"]
        elif "random-phases" in kargs:
            phases = [random.random() * math.pi * 2 for x in range(len(amplitudes))]
        else:
            phases = ZeroList([len(amplitudes)])
        
        if len(phases) != len(amplitudes):
            raise Exception("Number of phases must match the number of amplitudes")
        
        if "samples" in  kargs:
            self.samples = kargs["samples"]
            if self.samples <= 0:
                raise Exception("Samples must be a positive integer")
        else:
            self.samples = 4096

        self.cached_tables = CacheDict(50)
        
        self.harmonic_tables = ZeroList([len(amplitudes),self.samples])

        for amplitude, phase, harmonic, f in zip(amplitudes, phases, self.harmonic_tables, list(range(1,len(amplitudes)+1))):
            for sample in range(len(harmonic)):
                harmonic[sample] += amplitude * math.cos(phase + sample / self.samples * math.pi * 2 * f)
            max_amp = abs(max(harmonic))
            if max_amp != 0:
                harmonic = [x / max_amp for x in harmonic]
    def set_wave_table(self, frequency : float):
        """
        Sets the wave_table as to not include frequencies above the half sample rate
        """
        harmonics = int(((sample_rate // 2) - frequency) // frequency)

        harmonics = min(harmonics, len(self.harmonic_tables))

        if harmonics in self.cached_tables:
            self.wave_table = self.cached_tables[harmonics]
        
        else:
            new_table = ZeroList([self.samples])
            
            for harmonic in range(harmonics):
                new_table = [x + y for x,y in zip(new_table, self.harmonic_tables[harmonic])]
            self.wave_table = new_table
            self.cached_tables[harmonics] = new_table

    def get_samples(self, frequency : float, **kwargs):
        """
        Function used for sampling the wave table to get an output at a set frequency.

        Required arguments:
            frequency: the frequency in hertz of the output

            One length specifier from:
                samples: the length in samples of the output
                length: the length in seconds of the output
                periods: the length in periods at frequency
        Optional arguments:
            starting_phase: phase to start the output at in radians
                default: 0
            random_phase: boolean indicating if a random phase offset should be applied
                default: False
        """
        self.set_wave_table(frequency)

        return super().get_samples(frequency, **kwargs)
    
    def get_samples_bend(self, frequency1 : float, frequency2 : float, **kwargs):
        """
        Function used for sampling the wave table to get an output at a set frequency.

        Required arguments:
            frequency1: the frequency in hertz of the beginning of the ouput
            frequency2: the frequency in hertz of the end of the output

            One length specifier from:
                samples: the length in samples of the output
                length: the length in seconds of the output
        Optional arguments:
            starting_phase: phase to start the output at in radians
                default: 0
            random_phase: boolean indicating if a random phase offset should be applied
                default: False
        """

        self.set_wave_table(max(frequency1,frequency2))

        return super().get_samples_bend(frequency1, frequency2, **kwargs)

cos = WaveTable(math.cos, math.pi, sample_rate * 2)

saw = WaveTableHarmonic([1/n for n in range(1,1025)])

ocean_saw = WaveTableHarmonic([1/ (n ** 2) for n in range(1,1025)])

square = WaveTableHarmonic([(1/n if n % 2 == 1 else 0) for n in range(1,1025)])

