
import math

from .music import Note, Tempo

from .parameters import sample_rate

from .wavetable import WaveTableHarmonic

from .envelope import ADSR

class Instrument():
    def __init__(self):
        self.wave_table = WaveTableHarmonic([1 / (n) for n in range(1,100)])
        self.envelope = ADSR(25,50,0.7,50)
    def get_note_samples(self, note : Note):

        # get the length of the note in samples
        # sample_length = note.tempo.get_time(sum(note.length))
        # print(sample_length)

        output_samples = list()

        total_length = note.tempo.get_time(sum(note.length))

        if total_length < self.envelope.absolute_length:
            note.length[-1] += self.envelope.absolute_length - total_length

        for i, (length, pitch) in enumerate(zip(note.length,note.pitch)):
            if i < len(note.length) - 1:
                output_samples += self.wave_table.get_samples(440 * (2 ** ((pitch - 69) / 12)), samples = note.tempo.get_time(length) * 7 / 8)

                # print(output_samples)
                # return output_samples
                
                output_samples += self.wave_table.get_samples_bend(440 * (2 ** ((pitch - 69) / 12)), 440 * (2 ** ((note.pitch[i+1] - 69) / 12)), samples = note.tempo.get_time(length) / 8)
            else:
                output_samples += self.wave_table.get_samples(440 * (2 ** ((pitch - 69) / 12)), samples = note.tempo.get_time(length))
        
        output_samples = self.envelope.apply(output_samples)

        output_samples = [x * note.volume for x in output_samples]

        return output_samples

            


