import re
from collections import Counter

import numpy as np
import music21 as mu
mu.chord.Chord.priority = 15  # Should always come before notes played at same time

START = '>'
STOP = '!'

class ScoreProperties():
    """
    Get all properties of the score after transposing to C

    1. Key - use music21 analyze
    2. Chords:
        What chords
        What chords follow other chords
    3. Notes:
        What notes
        What notes played during a chord
        What notes follow other notes
    4. Durations:   N/A
        What durations
        What durations follow other durations
    """

    def __init__(self, score):

        for part in score.parts:
            if part.partName in ('Piano', 'Electric Organ', 'Drums'):
                score.remove(part)
                continue

            key = part.analyze('key')
            if 'minor' in str(key):
                key = key.relative
            part.transpose(-key.tonic.pitchClass, inPlace=True)
            part.chordify()

        self.score = score
        self.key = str(self.score.analyze('key'))

        self.chords = Counter()
        self.chord_graph = {'': Counter()}

        self.notes = Counter()
        self.note_graph = {'': Counter()}

        self.notes_in_chord = {'': Counter()}

        # Pass on durations

        # Valid chords
        #         C         Dm      Em       E        F        G         Am
        valid = { '0.4.7', '2.5.9', '2.5.7', '2.5.8', '0.5.9', '2.7.11', '0.4.9' }

        last_chord = ''
        last_note = ''
        for element in self.score.chordify().notesAndRests:
            if isinstance(element, mu.note.Rest):
                last_chord = ''
                last_note = ''

            elif isinstance(element, mu.note.Note):
                e = element.pitchClass
                self.notes.update([e])
                self.note_graph[last_note].update([e])
                self.notes_in_chord[last_chord].update([e])
                last_note = e
                if e not in self.note_graph:
                    self.note_graph[e] = Counter()

            elif len(element.normalOrder) < 3:
                e = [str(p) for p in element.normalOrder]
                self.notes.update(e)
                self.note_graph[last_note].update(e)
                self.notes_in_chord[last_chord].update(e)
                last_note = e[0]
                if e[0] not in self.note_graph:
                    self.note_graph[e[0]] = Counter()

            elif len(element.normalOrder) == 3:
                e = '.'.join([str(p) for p in sorted(element.normalOrder)])
                if e in valid:
                    self.chords.update([e])
                    self.chord_graph[last_chord].update([e])
                    last_chord = e
                    if e not in self.chord_graph:
                        self.chord_graph[e] = Counter()
                        self.notes_in_chord[e] = Counter()


        for note in self.note_graph:
            del self.note_graph[note][note]

        for chord in self.chord_graph:
            del self.chord_graph[chord][chord]


    @property
    def first_chords(self):
        return self.chord_graph[''] + self.chords[max(self.chords)]

    @property
    def first_notes(self):
        return self.note_graph[''] + self.notes[max(self.notes)]


class Analysis():

    """ Merge score properties into one analysis """
    def __init__(self):
        self.score_properties = []

    def load(self, artist):
        pass

    def init(self, scores):
        self.score_properties = [ ScoreProperties(sc) for sc in scores ]

    def __iter__(self):
        return iter(self.score_properties)


    """ Random choices """

    def randomElementFromCounter(self, counter, n=10):
        elements, appearences = zip(*counter.most_common(n))
        p = sum(appearences)
        return np.random.choice(elements, p=[a/p for a in appearences])


    def randomKey(self):
        return self.randomElementFromCounter(self.keys)

    def randomMode(self, key):
        return self.randomElementFromCounter(self.modes_in_key[key])

    def randomChord(self, key):
        return self.randomElementFromCounter(self.chords_in_key[key])

    def randomChordProgression(self, key, mode=0, length=np.random.randint(4,8)):
        progression = [self.randomChord(key)]
        chord_graph = self.chord_graph
        for _ in range(length-1):
            last = progression[-1]
            progression.append(self.randomElementFromCounter(chord_graph[last]))
        return progression


    def randomNote(self, chord):
        if chord in self.notes_in_chord:
            return self.randomElementFromCounter(self.notes_in_chord[chord])
        else:
            return np.random.choice(chord.split('.'))

    def samples(self):
        return [ [ [pitch.pitchClass for pitch in n.pitches] for n in part.chordify().notes] for sc in self for part in sc.score.parts ]


    def smooth(self, note, bad):
        if bad in self.note_graph[note]:
            return [bad]
        else:
            transition = []
            for n in self.note_graph:
                if bad in self.note_graph[note]:
                    return [ n, bad, self.randomElementFromCounter(self.note_graph[note]) ]
        return self.randomElementFromCounter(self.note_graph[note])



    """ Properties """

    @property
    def keys(self):
        return Counter([sp.key for sp in self])

    @property
    def modes_in_key(self):
        return self.key_counters([ (sp.key, sp.first_notes) for sp in self ])

    @property
    def notes(self):
        return self.merge_counters([sp.notes for sp in self])

    @property
    def note_graph(self):
        return self.graph([sp.note_graph for sp in self])

    @property
    def notes_in_chord(self):
        return self.key_counters([ (key,counter) for sp in self for key,counter in sp.notes_in_chord.items() ])

    @property
    def chords(self):
        return self.merge_counters([sp.chords for sp in self])

    @property
    def chords_in_key(self):
        return self.key_counters([ (sp.key, sp.chords) for sp in self ])

    @property
    def chord_graph(self):
        return self.graph([sp.chord_graph for sp in self])


    """ Decided against
    @property
    def durations(self):
        return self.merge_counters([sp.durations for sp in self])

    @property
    def duration_graph(self):
        return self.graph([sp.duration_graph for sp in self])

    """

    """ Helpers """

    def merge_counters(self, counters):
        total = Counter()
        for counter in counters:
            total += counter
        return total

    def key_counters(self, pairs):
        mapping = {}
        for key, counter in pairs:
            if len(counter):
                if key not in mapping:
                    mapping[key] = counter
                else:
                    mapping[key] += counter
        return mapping

    def graph(self, graphs):
        total = {}
        for graph in graphs:
            for node in graph:
                if node not in total:
                    total[node] = graph[node]
                else:
                    total[node].update(graph[node])
        return total



    def fromJSON(self, _json):
        pass

    def toJSON(self):
        pass


