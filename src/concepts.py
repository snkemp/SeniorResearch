"""
A file to help create musical concepts.

"""
import json
import pprint
log = pprint.PrettyPrinter(indent=4).pprint

class Concept():

    def __init__(self, note, index):
        self.note = note
        self.index = index
        self.child = False

        self.notes = [note]

    def __str__(self):
        return str(self.note)

    def __repr__(self):
        return "Concept:\n\t\t" + "\n\t\t".join( map(str, self(1)) ) + " >"

    def __call__(self, *args):
        if args:
            return self.notes

        return self.note

    def __int__(self):
        return self.index

    def __bool__(self):
        return self.child

    def __iadd__(self, other):
        self.notes += other.notes
        self.child = other.child
        return self

    def __eq__(self, other):
        return repr(self) == repr(other)


class Field():
    """

    [ 2. 3. 4. 2. 3. 2. 3. 4. 5. 4. 5 ]
    [ 2.3.4, 2.3, 2.3.4.5, 4.5 ]

    """

    def __init__(self, part):

        # Disjoint set
        notes = [ Concept(note, i) for i, note in enumerate(part.notesAndRests) ]
        indices = {}

        # Save indices of each note into a dict
        for note in notes[:-2]:
            if str(note) not in indices:
                indices[str(note)] = list()
            indices[str(note)].append(int(note))

        log(indices); print()
        # For each type of note
        for ix in indices:

            # Ignore unique notes
            if len(indices[ix]) <= 1:
                continue

            # Store indices of each kind of successive note
            jndices = {}
            for note in map(lambda i: notes[i+1], indices[ix]):
                 if str(note) not in jndices:
                     jndices[str(note)] = list()
                 jndices[str(note)].append(int(note))

            # Ignore notes that always goto the same note
            if len(jndices) <= 1:
                continue

            # Mark most common instance of successive note (ignore only one)
            most = max(jndices, key=lambda x: len(jndices[x]))

            # Each note with respective successive note should be combined later
            for jx in jndices[most]:
                notes[jx-1].child = True


        # Create concepts from our
        self.concepts = [ notes[0] ]
        for i in range(1, len(notes)):
            if self.concepts[-1].child:
                self.concepts[-1] += notes[i]
            else:
                self.concepts.append(notes[i])


    def __str__(self):
        return '\tField: \n\t' + '\n\t'.join(map(repr, self.concepts))




class Composition():

    def __init__(self, score):
        self.fields = [ Field(part) for part in score.parts ]

    def __str__(self):
        return 'Composition:\n' + '\n'.join(map(str, self.fields))



def conceptualize(score):
    """ Converts a score or a list of scores into fields """

    if isinstance(score, list):
        return [ conceptualize(sc) for sc in score ]

    return Composition(score)
