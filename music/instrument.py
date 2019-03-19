
import math

class Instrument():
    def __init__(self):
        self.wave_table = [math.cos(math.pi*2*x/4096) + math.cos(math.pi*2*x*2/4096) for x in range(4096)]
    def get_note_samples(self, note: Note):

        # get the length of the note in samples
        sample_length = note.bpm/60*note.duration*note.sample_rate

        ouput_samples = list()

        for sample_index in range(sample_length):
            output_samples = list