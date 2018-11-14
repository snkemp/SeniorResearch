"""
"""


import music21 as mu
from src.music import conceptualize
import numpy as np

class Score():

    def __init__(self, score):

        self.fileName = score
        self.score = mu.converter.parse(score)
        for part in self.score.parts:
            key = part.analyze('key')

            if 'minor' in str(key):
                key = key.relative

            toC = 60 - key.tonic.midi
            part.transpose(toC, inPlace=True)


        self._melody = None
        self._harmony = None


    def getMelodyPart(self):
        for p in self.score.parts:
            if p.partName == 'Saxophone':
                return p
        return self.score.parts[0]

    def getHarmonyPart(self):
        return self.score.parts[0]


    @property
    def melody(self):
        if not self._melody:
            self._melody = self.getMelodyPart()

        return [ note.pitches for note in self._melody.notes ]


    @property
    def harmony(self):
        if not self._harmony:
            self._harmony = self.getHarmonyPart()

        return [ chord.pitches for chord in self._harmony.notes ]


    def __str__(self):
        return self.fileName

    def toJSON(self):
        return str(self)

    def fromJSON(self, string):
        self.__init__(string)
        return self


class Opus():

    def __init__(self, scores):
        self.scores = [ Score(sc) for sc in scores ]

        self.melodies = [ sc.melody for sc in self.scores ]
        self.harmonies = [ sc.harmony for sc in self.scores ]

        self.notes = [ pitches[0].pitchClass for melody in self.melodies for pitches in melody ]
        self.uniqueNotes = sorted(set(self.notes))

        self.chords = [ mu.chord.Chord(pitches).normalOrderString for harmony in self.harmonies for pitches in harmony ]
        self.uniqueChords = sorted(set(self.chords))

        self.index_to_note = dict(enumerate(self.uniqueNotes))
        self.note_to_index = { k:i for i,k in enumerate(self.uniqueNotes) }

        self.index_to_chord = dict(enumerate(self.uniqueChords))
        self.chord_to_index = { k:i for i,k in enumerate(self.uniqueChords) }

        self.concepts = conceptualize(self.scores)

    def toJSON(self):
        return str(self)

    def fromJSON(self, string):
        self.__init__(string.split('<?>'))
        return self

    def __str__(self):
        return "<?>".join([ sc.toJSON() for sc in self.scores ])

    @property
    def numNotes(self):
        return len(self.uniqueNotes)

    @property
    def numChords(self):
        return len(self.uniqueChords)

