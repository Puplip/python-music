
from .parameters import sample_rate
from .instrument import Instrument
import scipy.io.wavfile as wav

from mido import MidiFile, tempo2bpm, tick2second

from .music import Note, Tempo, Track
from .utils import *
import numpy as np
import math

class MidiTempo(Tempo):
    """
    Tempo used for midi files. Used for automatic Midi Tick (beat) to sample conversion.

    Arguments:
        tempo: midi tempo in mico-seconds per beat
        tpb: midi ticks per beat
    """
    def __init__(self, start_tick : int, start_sample : float, tempo : float, tpb : float):
        self.bpm = tempo2bpm(tempo)
        self.beat_samples = sample_rate / 1000000 * tempo / tpb
        self.start_tick = start_tick
        self.start_sample = start_sample

class SampleTempo(Tempo):
    """
    Tempo where 1 beat = 1 sample

    Arguments:
        tempo: midi tempo in mico-seconds per beat
        tpb: midi ticks per beat
    """
    def __init__(self):
        self.bpm = sample_rate * 60
        self.beat_samples = 1

class Midi():
    """
    Creates an interface for reading and synthesizing midi files.

    filename: name of the midi file to open
    """

    sample_tempo = SampleTempo()

    def __init__(self, filename : str):
        self.midifile = MidiFile(filename)
        

        self.tempos = list()

        for msg in self.midifile.tracks[0]:
            if msg.type == "set_tempo":
                if msg.time == 0:
                    self.tempos.append(MidiTempo(0, 0, msg.tempo, self.midifile.ticks_per_beat))
                else:
                    self.tempos.append(MidiTempo(self.tempos[-1].start_tick + msg.time, self.tempos[-1].start_sample + self.tempos[-1].get_time(msg.time) , msg.tempo, self.midifile.ticks_per_beat))
                # print(msg.time)
                # print(self.tempos[-1].start_tick)
                # print(self.tempos[-1].start_sample)
        

        for i, track in enumerate(self.midifile.tracks):
            time = 0
            for msg in track:
                time += msg.time
                msg.time = time

        open_notes = dict()

        self.track_notes = NoneList([len(self.midifile.tracks),0])

        for i, track in enumerate(self.midifile.tracks):
            if i is not 0:
                for msg in track:
                    if msg.type == "note_on":
                        open_notes[msg.note] = msg
                    elif msg.type == "note_off":
                        start_sample = self.tick2sample(open_notes[msg.note].time)
                        self.track_notes[i].append(Note(Midi.sample_tempo,start_sample,[self.tick2sample(msg.time) - start_sample],[msg.note],open_notes[msg.note].velocity / 127))
    
    def tick2sample(self,tick : float):

        last_tempo = None

        for tempo in self.tempos:
            if tempo.start_tick > tick:
                break
            last_tempo = tempo

        return last_tempo.start_sample + last_tempo.get_time(tick - last_tempo.start_tick)
    
    def synth(self, filename : str, instruments : List[Instrument]):

        output_tracks = list()

        for instrument, track in zip(instruments, self.track_notes):
            new_track = Track()
            for note in track:
                new_track.add_sound(instrument.get_note_samples(note), int(note.beat))
            output_tracks.append(new_track)
        
        mixed_track = Track.mix(output_tracks, [1 / len(output_tracks) for x in output_tracks])
        
        mixed_track.normalize()

        wav.write(filename, sample_rate, np.array(mixed_track.data))