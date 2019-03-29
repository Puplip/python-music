import music

import scipy.io.wavfile as wav
import numpy as np

if __name__ == "__main__":
    tempo = music.Tempo(120)
    note_b = music.Note(tempo,0,[0.5],[69])
    note_t = music.Note(tempo,0,[0.5],[76])
    instrument = music.Instrument()
    note_samples_b = list()
    note_samples_t = list()

    for i in range(16):
        note_samples_b += instrument.get_note_samples(note_b)
    
    for i in range(16):
        note_samples_t += instrument.get_note_samples(note_t)
    
    mixed_samples = list()

    for s0, s1 in zip(note_samples_b, note_samples_t):
        mixed_samples.append(s0 * 0.5 + s1 * 0.5)

    wav.write("test_output.wav", music.sample_rate, np.array(mixed_samples))

