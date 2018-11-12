"""
"""

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

    def __init__(self, notes):
        pass


class Melody():

    def __init__(self, notes):
        pass


class Harmony():

    A_MINOR = { 'C', 'Dm', 'Em', 'F', 'G', 'Am' }
    C_MAJOR = { 'C', 'E', 'E7', 'F', 'G', 'Am' }
    F_MAJOR = { 'C', 'Em', 'F', 'G7', 'Am', 'B-' }
    G_MAJOR = { 'C', 'D', 'Em', 'G', 'Am', 'Bm' }

    CHORDS = Harmony.A_MINOR | Harmony.C_MAJOR | Harmony.F_MAJOR | Harmony.G_MAJOR

    def __init__(self, melody):
        pass
