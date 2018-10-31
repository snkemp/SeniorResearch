"""
A file to help create musical concepts.

"""

import json
import heapq
import music21 as mu

class Concept():

    def __init__(self, note, index):
        self.index = index
        self.child = False

        self.notes = [note]


    @property
    def note(self):
        return self.notes[0]

    @property
    def merge(self):
        return self.child and not isinstance(self.note, mu.note.Rest)


    def __int__(self):
        return self.index

    def __str__(self):
        return '<Concept ' + ', '.join( map(str, self()) ) + ' >'

    def __repr__(self):
        return "Concept:\n\t\t" + "\n\t\t".join( map(str, self()) )


    def __call__(self):
        return self.notes


    def __bool__(self):
        return self.child

    def __iadd__(self, other):
        self.notes += other.notes
        self.child = other.child
        return self

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))


Concept.NONE = Concept('NONE', -1)
Concept.BEGINNING = Concept('BEG', -2)
Concept.END = Concept('END', -3)

class TableEntry():

    def __init__(self):
        self.indices = []
        self.next = {}

    def update(self, concept, next_concept):
        self.indices.append(int(concept))

        if next_concept not in self.next:
            self.next[next_concept] = []

        self.next[next_concept].append(int(next_concept))

    def most(self):
        key = lambda x: len(self.next[x])
        most_common = max(self.next, key=key)
        frequency = key(most_common)
        ratio = .85*frequency

        return [ i for mc in sorted(
                                filter(lambda x: key(x) > ratio, self.next),
                                key=key) for i in self.next[mc] ]


    def __iter__(self):
        return iter(self.most())


class IndexTable():

    def __init__(self):
        self.indices = {}


    def update(self, concept, next_concept):
        if concept not in self.indices:
            self.indices[concept] = TableEntry()

        self.indices[concept].update(concept, next_concept)


    def __iter__(self):
        for concept in self.indices:
            yield self.indices[concept]


class Field():
    """

    [ 2. 3. 4. 2. 3. 2. 3. 4. 5. 4. 5 ]
    [ 2.3.4, 2.3, 2.3.4.5, 4.5 ]

    """

    def __init__(self, part):

        # Disjoint set
        notes = [Concept.BEGINNING] + [ Concept(note, i+1) for i, note in enumerate(part.notesAndRests) ] + [Concept.END]

        # Save indices of each note into a dict
        table = IndexTable()
        for i in range(1, len(notes)-1):
            table.update(notes[i], notes[i+1])


        for entry in table:
            for i in entry:
                notes[i-1].child = True

        # Group concepts
        self.concepts = [ notes[0] ]
        for note in notes[1:]:
            if self.concepts[-1].merge:
                self.concepts[-1] += note
            else:
                self.concepts.append(note)


    def __str__(self):
        return '\tField: \n\t' + '\n\t'.join(map(repr, self.concepts))


    def __iter__(self):
        return iter(self.concepts)


    @property
    def corpus(self):
        return set(self.concepts)

    @property
    def data(self):
        return self.concepts


class Composition():

    def __init__(self, score):
        self.fields = [ Field(part) for part in score.parts ]

    def __str__(self):
        return 'Composition:\n' + '\n'.join(map(str, self.fields))


    def __iter__(self):
        return iter(self.fields)

    @property
    def corpus(self):
        return set().union(*[field.corpus for field in self])

    @property
    def data(self):
        return [ concept for field in self for concept in field ]



def conceptualize(score):
    """ Converts a score or a list of scores into fields """

    if isinstance(score, list):
        return [ conceptualize(sc) for sc in score ]

    return Composition(score)
