"""
A file to help create musical concepts.

"""

import json
import music21 as mu

class Concept():

    def __init__(self, note, index):
        self.index = index
        self.child = False

        self.notes = [note]


    @property
    def note(self):
        return self.notes[0]



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



class Field():
    """

    [ 2. 3. 4. 2. 3. 2. 3. 4. 5. 4. 5 ]
    [ 2.3.4, 2.3, 2.3.4.5, 4.5 ]

    """

    def __init__(self, part):

        # Disjoint set
        notes = [Concept.BEGINNING] + [ Concept(note, i+1) for i, note in enumerate(part.notesAndRests) ] + [Concept.END]

        # Save indices of each note into a dict
        indices = {}
        for note in notes[1:-2]:
            if note not in indices:
                indices[note] = list()
            indices[note].append(int(note))

        # For each type of note
        for concept in indices:

            # Ignore unique notes
            if len(indices[concept]) <= 1 or isinstance(concept.note, mu.note.Rest):
                continue

            # Store indices of each kind of successive note
            jndices = {}
            for ix in indices[concept]:
                note = notes[ix+1]
                if note not in jndices:
                    jndices[note] = list()
                jndices[note].append(int(note))

            # Ignore notes that always goto the same note
            # if len(jndices) <= 1:
            #     continue

            # Mark most common instance of successive note
            most_common = max(jndices, key=lambda c: len(jndices[c]))

            # Each note with respective successive note should be combined later
            for jx in jndices[most_common]:
                notes[jx-1].child = True


        # Group concepts
        self.concepts = [ notes[0] ]
        for note in notes[1:]:
            if self.concepts[-1].child:
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
