import re
from collections import Counter

import numpy as np

import music21 as mu

START = '[START]'
STOP = '[STOP]'

def encode(note):
    if isinstance(note, mu.note.Note) or isinstance(note, mu.chord.Chord):
        return [ p.pitchClass for p in note.pitches ]
    elif isinstance(note, mu.note.Rest):
        return [12]
    elif note == START:
        return [13]
    elif note == STOP:
        return [14]
    else:
        raise Exception('Cant encode illegal argument: %s' % str(note))


def decode(note):
    if note < 0:
        raise Exception('Cannot decode illegal argument: %s' % str(note))
    elif note < 12:
        return mu.note.Note(note)
    elif note == 12:
        return mu.note.Rest()
    elif note == 13:
        return START
    elif note == 14:
        return STOP
    raise Exception('Cannot decode illegal argument: %s' % str(note))


class Analysis():

    def __init__(self, *args):
        self.chords_in_key, self.notes_during_chord, self.chord_graph, self.first_chords, self.note_graph, self.first_notes, *rest = args

    def __str__(self):
        return '\n'.join([
            'Keys:  \t' + str(self.chords_in_key),
            'Chords:\t' + str(self.chord_graph),
            'Notes: \t' + str(self.note_graph)
            ])




    def randomKey(self):
        return np.random.choice(list(self.chords_in_key.keys()))

    def randomFirstChord(self, key):
        valid_chords = set(self.chords_in_key[key].keys()) & self.first_chords & set(self.chord_graph.keys())
        return np.random.choice(list(valid_chords))

    def randomChordProgression(self, key, n=20):
        starting_chord = self.randomFirstChord(key)
        curr_chord = starting_chord

        for _ in range(n):
            yield curr_chord

            if curr_chord not in self.chord_graph:
                curr_chord = self.randomFirstChord(key)

            chords = list(self.chord_graph[curr_chord].elements())  # [ 'C', 'C', 'G' ... ] Duplicates are in there so probablities are inherent
            curr_chord = np.random.choice(chords)

        return curr_chord


    def randomFirstNote(self, chord):
        valid_notes = set(self.notes_during_chord[chord].keys()) & self.first_notes & set(self.note_graph.keys())
        return np.random.choice(list(valid_notes))




def conceptualize(artist):
    """
    Given an artist we want to find out a few things

    1. Find chords played in a key
    2. Find notes played in a key
    2. Find the set of notes played during each chord and how often
    3. Create chord graph
    4. Create note graph
    """

    chord_in_key = {}

    notes_during_chord = {}

    chord_graph = {}
    first_chords = set()

    note_graph = {}
    first_notes = set()


    for song in artist.works:


        # 1
        key = song.key.tonicPitchNameWithCase
        if not key in chord_in_key:
            chord_in_key[key] = Counter()
        chord_in_key[key] += Counter([chord.normalOrderString for part in song.chords for chord in part])


        # 2
        for notes, chord in song.noteChordPairings:
            if chord not in notes_during_chord:
                notes_during_chord[chord] = Counter()

            notes_during_chord[chord] += Counter(notes)

        # 3
        for progression in song.chords:
            if not progression:
                continue

            last = progression[0].normalOrderString
            first_chords |= {last}
            for chord in progression[1:]:
                chord = chord.normalOrderString

                if last not in chord_graph:
                    chord_graph[last] = Counter()
                chord_graph[last] += Counter([chord])
                last = chord

        # 4
        for melody in song.notes:
            if not melody:
                continue

            last = melody[0].name
            first_notes |= {last}
            for note in melody[1:]:
                note = note.name

                if last not in note_graph:
                    note_graph[last] = Counter()
                note_graph[last] += Counter([note])
                last = note


    return Analysis(chord_in_key, notes_during_chord, chord_graph, first_chords, note_graph, first_notes)
