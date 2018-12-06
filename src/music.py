"""
Handles music theory side of things

"""

from glob import glob

import numpy as np
import music21 as mu
mu.chord.Chord.priority = 15  # Should come before notes (20)

from collections import Counter

from src.concepts import Analysis


class Artist():


    def __init__(self):
        self.analysis = Analysis()

    def init(self, artist):
        self.artist = artist

        self.works = [ mu.converter.parse(f) for f in glob('data/%s/*.midi' % artist) ]
        self.compositions = [ mu.converter.parse(f) for f in sorted(glob('output/%s/*.midi' % artist)) ]

        notes = []
        for sc in self.works:
            for part in sc.parts:
                if part.partName in ('Piano', 'Electric Organ', 'Drums'):
                    continue

                key = part.analyze('key')
                if 'minor' in str(key):
                    key = key.relative

                notes.append('START')
                for e in part.flat.transpose(-key.tonic.pitchClass).notes:
                    notes.append('.'.join(set([str(p.pitchClass) for p in e.pitches])))

                notes.append('END')

        self.notes = notes
        self.analysis.init(self.works)

    def load(self, artist):
        #TODO
        self.init(artist)

    def save(self):
        for i,comp in enumerate(self.compositions):
            mf = mu.midi.translate.streamToMidiFile(comp)
            mf.open('output/%s/track%d.midi' % (self.artist, i), 'wb')
            mf.write()
            mf.close()


    def add(self, composition):
        self.compositions.append(composition.score)




class Composition():

    def __init__(self, artist, network):

        self.artist = artist
        self.network = network

        self.key = artist.analysis.randomKey()
        self.mode = artist.analysis.randomMode(self.key)

        self.chord_progression = artist.analysis.randomChordProgression(self.key, self.mode)
        self.notes = []

        bad = {'1','3','6','8','10'}

        self.measures = []
        for chord in self.chord_progression:
            cnote = artist.analysis.randomNote(chord)
            notes = [cnote]

            self.notes.append(cnote)
            for _ in range(np.random.randint(6,10)):
                _n = network.predict(self.notes)
                for n in _n.split('.'):
                    if n in bad:
                        for note in artist.analysis.smooth(notes[-1], n):
                            self.notes.append(note)
                            notes.append(n)
                    else:
                        self.notes.append(n)
                        notes.append(n)

            self.measures.append((chord, notes))


        self.populateMeasures()
        self.buildStream()


    def populateMeasures(self):

        """ Rules
        +n : number of times note appears in all measures
        +2 : if note in chord
        +1 : if note in previous or next chord
        -k : number of times note appears in this measure - 1 (dont count this instance it's not its fault it appears)
        """

        total_notes = Counter([ n for h,m in self.measures for n in m ])
        measure_notes = [ Counter(m) for h,m in self.measures ]

        print(total_notes)
        print(measure_notes)

        n = len(self.measures)
        N = lambda x: x+1 if x < n-1 else 0
        P = lambda x: x-1 if x > 0 else -1

        penta = {'0', '4', '5', '7', '9'}
        bad = { '1', '3', '6', '8', '10' }


        populations = []
        for i, measure in enumerate(self.measures):
            curr, notes = measure

            _prev, _ = self.measures[P(i)]
            _next, _ = self.measures[N(i)]

            # Calculate popularity
            popularity = []
            for note in notes:
                pop = 1 + total_notes[note] - measure_notes[i][note]

                if note in curr:
                    pop += 3
                if note in _prev:
                    pop += 1
                if note in _next:
                    pop += 1
                if note in penta:
                    pop += 2
                if note in bad:
                    pop -= 1

                popularity.append(pop)

            T = sum(popularity)
            notes_and_rests = []
            chords = [(curr,4) for _ in range(4)]

            total = 0
            rest = 0
            for i, note in enumerate(notes):
                dur = round((16*popularity[i])/T)
                total += dur
                notes_and_rests.append((note,dur))

            if total < 16:
                notes_and_rests.append((None, 16-total))
            elif total > 16:
                index, e = max([ (_i, _e) for _i,_e in enumerate(notes_and_rests) ], key=lambda x: x[1][1])
                _e, _d = e
                notes_and_rests[index] = _e, _d-total+16

            print(notes_and_rests)
            populations.append((chords, notes_and_rests))

        self.measures = populations


    def buildStream(self):
        score = mu.stream.Score()
        score.insert(mu.tempo.MetronomeMark(number=400))

        har = mu.stream.Part()
        har.insert(mu.instrument.Guitar())

        mel = mu.stream.Part()
        mel.insert(mu.instrument.Trumpet())

        for chords, notes in self.measures:
            _har = mu.stream.Voice()
            for ch,dur in chords:
                chord = mu.chord.Chord([int(p) for p in ch.split('.')])
                chord.quarterLength = dur
                _har.append(chord)

            _mel = mu.stream.Voice()
            for n, dur in notes:
                if n:
                    note = mu.note.Note(int(n))
                    if n == '11' or n == '10' or n == '9':
                        note.octave = 3

                else:
                    note = mu.note.Rest()

                note.quarterLength = dur
                _mel.append(note)

            har.append(_har)
            mel.append(_mel)

        score.insert(mel)
        score.insert(har)

        self.score = score
