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



    def clean(self, notes):

        composition = [notes[0]]
        note_name = ('C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 'C5')
        for note in notes[1:]:
            if self.badInterval(composition[-1], note):
                bridge = self.bridgeInterval(composition[-1], note)
                print('Bad interval: %d, %d inserting %s' % (composition[-1], note, str(bridge)))
            else:
                composition.append(note)

        score = mu.stream.Score()

        mel = mu.stream.Part()
        mel.insert(mu.instrument.Trumpet())

        for note in composition:
            mel.append(mu.note.Note(name=note_name[note]))


        har = mu.stream.Part()
        har.insert(mu.instrument.Guitar())

        score.insert(mel)
        score.insert(har)

        return score

    def badNote(self, note):
        return note in (1, 3, 6, 10)


    def badInterval(self, fr, to):
        return fr != to and (self.badNote(fr) or self.badNote(to) or (fr,to) in [(0,11), (11,0)])


    def bridgeInterval(self, fr, to):
        bridges = self.concepts.match(fr, to)
        if len(bridges) == 0:
            return self.bridgeInterval(fr, (fr+to)//2) + self.bridgeInterval((fr+to)//2, to)
        i = np.random.choice(list(range(len(bridges))))
        return bridges[i]

