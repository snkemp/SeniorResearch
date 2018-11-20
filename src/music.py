"""
Handles music theory side of things

"""

from glob import glob

import numpy as np
import music21 as mu
mu.chord.Chord.priority = 15  # Should come before notes (20)

from src.concepts import conceptualize, encode, decode, START, STOP

class Song():

    def __init__(self, song):
        self.song = song
        self.composition = mu.converter.parse(song)

        for part in self.composition:
            key = part.analyze('key')
            if str(key) in ('C major', 'a minor'):
                continue

            if 'minor' in str(key):
                key = key.relative

            toC = -key.tonic.pitchClass
            part.transpose(toC, inPlace=True)

        self.key = self.composition.analyze('key')

    @property
    def notes(self):
        return [ [ note for note in part if isinstance(note, mu.note.Note) ] for part in self.composition.parts ]

    @property
    def chords(self):
        return [ [ chord for chord in part if isinstance(chord, mu.chord.Chord) ] for part in self.composition.parts ]

    @property
    def data(self):
        return [ note for note in self.composition.flat.notesAndRests ]


    @property
    def noteChordPairings(self):
        last_chord = mu.chord.Chord(mu.harmony.ChordSymbol('C'))
        pairings = [ [[],last_chord.normalOrderString] ]

        for note in self.data:
            if isinstance(note, mu.note.Rest):
                pairings.append([[], ''])

            elif isinstance(note, mu.note.Note):
                pairings[-1][0].append(note.name)

            elif isinstance(note, mu.chord.Chord):
                if note.normalOrderString != last_chord.normalOrderString:
                    pairings.append([[], last_chord.normalOrderString])
                last_chord = note

        return pairings



class Artist():


    def __init__(self, artist=None):
        if artist:
            self.init(artist)

    def init(self, artist):
        self.artist = artist

        self.works = [ Song(f) for f in glob('data/%s/*.midi' % artist) ]
        self.compositions = [ mu.converter.parse(f) for f in glob('output/%s/*.midi' % artist) ]

        self.analysis = conceptualize(self)

    def load(self, artist):
        #TODO
        self.init(artist)

    def save(self):
        for i,comp in enumerate(self.compositions):
            mf = mu.midi.translate.streamToMidiFile(comp)
            mf.open('output/%s/track%d.midi' % (self.artist, i), 'wb')
            mf.write()
            mf.close()


    def add(self, compositions):
        self.compositions += compositions


    def compose(self, network):

        key = self.analysis.randomKey()
        pairings = []

        for chord in self.analysis.randomChordProgression(key, 4):
            #starting_note = mu.note.Note(self.analysis.randomFirstNote(chord)).pitch.pitchClass
            starting_note = encode(START)

            melody = network.predict(starting_note, 50)
            chord = mu.chord.Chord([ int(p, 16) for p in chord[1:-1] ])

            pairings.append((chord, melody))

        print(pairings)

        score = mu.stream.Score()
        score.insert(mu.key.Key(key))

        mel = mu.stream.Part()
        mel.insert(mu.instrument.Trumpet())

        har = mu.stream.Part()
        har.insert(mu.instrument.Guitar())

        for chord, melody in pairings:
            har.append(chord)
            for note in melody:
                if note == 12:
                    note = mu.note.Rest()
                else:
                    note = mu.note.Note(note)
                mel.append(note)

        score.insert(har)
        score.insert(mel)

        self.compositions.append(score)
        return key, score.analyze('key'), [ chord for chord, melody in pairings ], set([note for chord, melody in pairings for note in melody])

    @property
    def training_data(self):
        seq_len = 50

        data = []
        for part in [ p for song in self.works for p in song.composition.parts ]:

            long_sequence = list(part.flat.notesAndRests)
            sequence = [encode(START)]
            for n in long_sequence:
                if isinstance(n, mu.note.Rest) and n.duration.quarterLength < 4:
                    continue

                sequence.append(encode(n))
            sequence.append(encode(STOP))

            n = len(sequence)
            dX = [ sequence[i:i+seq_len] for i in range(n - seq_len) ]
            dY = [ sequence[i+seq_len] for i in range(n - seq_len) ]

            dataX = [ [ [ i in k for i in range(15) ] for k in sdx ] for sdx in dX ]
            dataY = [ [ i in k for i in range(15) ] for k in dY ]

            x = np.reshape(dataX, (len(dataX), seq_len, 15))
            y = np.reshape(dataY, (len(dataY), 1, 15))

            data.append((x,y))

        return data

    @property
    def data(self):
        return [ song.data for song in self.works ]


    @property
    def notes(self):
        return [ song.notes for song in self.works ]

    @property
    def uniqueNotes(self):
        return { note.name for sequence in self.notes for note in sequence }

    @property
    def chords(self):
        return [ song.chords for song in self.works ]

    @property
    def uniqueChords(self):
        return { chord.normalOrderString for progression in self.chords for chord in progression }

    @property
    def keys(self):
        return [ song.key for song in self.works ]

    @property
    def uniqueKeys(self):
        return { (key.tonic, key.mode) for key in self.keys }
