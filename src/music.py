"""
"""

import numpy as np
import music21 as mu

class ConceptTable():

    def __init__(self, scores):

        self.sequences = [ [ pitches[0].pitchClass for pitches in score.melody ] for score in scores ]
        self.pointers = { i: { j: [] for j in range(12) } for i in range(12) }

        for i, melody in enumerate(self.sequences):
            for j, note in enumerate(melody[:-1]):
                self.pointers[note][melody[j+1]].append((i,j))


    def match(self, fr, to):
        indices = self.pointers[fr][to]
        return [ self.sequences[i][j:j+4] for i, j in indices ]




def conceptualize(scores):

    table = ConceptTable(scores)
    return table



class Composition():

    def __init__(self):

        self.harmony = Harmony()
        self.melody  = Melody()

    def compose(self, network):
        self.harmony.__init__()
        self.melody.__init__()

        return self.score(network)

    def score(self, network):

        sc = mu.stream.Score()

        har = mu.stream.Part()
        har.insert(mu.instrument.Piano())

        mel = mu.stream.Part()
        mel.insert(mu.instrument.Trumpet())

        har.append(self.harmony.progression())
        mel.append(self.melody.sequence(self.harmony, network))

        sc.insert(har)
        sc.insert(mel)

        sc.show('t')
        return sc



class Melody():

    def __init__(self):
        pass

    def sequence(self, harmony, network):

        sequence = network.generateMelody(harmony, self)
        print(sequence)

        ns = mu.stream.Voice()
        for note in sequence:
            ns.append(mu.note.Note(note, quarterLength=max(.25, 32/len(sequence))))

        return ns


class Harmony():

    # Chords
    A_MINOR = [ 'C', 'Dm', 'E7', 'F', 'G', 'Am' ]
    C_MAJOR = [ 'C', 'E7', 'F', 'G', 'Am' ]
    F_MAJOR = [ 'C', 'Em', 'F', 'G7', 'Am', 'B-' ]
    G_MAJOR = [ 'C', 'D', 'Em', 'G', 'Am', 'Bm' ]
    CHORDS = [ A_MINOR, C_MAJOR, F_MAJOR, G_MAJOR ]


    # Rythym
    STACCATO = 0
    LEGATO = 1
    RYTHYM = [ STACCATO, LEGATO ]

    def __init__(self):

        self.rythym_type = np.random.choice(Harmony.RYTHYM, p=[.6, .4])

        d = list(range(16))
        np.random.shuffle(d)
        self.rythym_db = sorted(d[: np.random.randint(5,9) ])

        chord_set = np.random.choice([ i for i,k in enumerate(Harmony.CHORDS)])
        self.chord_set = Harmony.CHORDS[chord_set]

        self._progression = None


    def randomProgression(self):
        return np.random.choice( self.chord_set, np.random.randint(4, 7) )

    def randomStartingNote(self, chord):

        chord = mu.chord.Chord(mu.harmony.ChordSymbol(chord))
        return chord.root().pitchClass

    def progression(self):
        if not self._progression:
            self._progression = self.randomProgression()


        duration = [ (n-p) for p,n in zip(self.rythym_db, self.rythym_db[1:] + [16]) ]

        cp = mu.stream.Voice()
        for chord in self._progression:

            if self.rythym_type == Harmony.LEGATO:
                pitches = mu.harmony.ChordSymbol(chord).pitches
                notes = [ p for p in np.random.choice(pitches, len(self.rythym_db)) ]

                for n,d in zip(notes, duration):
                    cp.append(mu.note.Note(n, quarterLength=d/16))

            else:
                for d in duration:
                    cp.append(mu.chord.Chord(mu.harmony.ChordSymbol(chord), quarterLength=max(.25, d/16)))


        return cp


    def __len__(self):
        return len(self._progression)

    def __iter__(self):
        return iter(self._progression)


