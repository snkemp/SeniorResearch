"""
"""

import re, json

import numpy as np
np.random.seed(73)

from keras.models import Sequential, model_from_json
from keras.layers import Input, Dense, Activation, LSTM, TimeDistributed, Flatten


from itertools import groupby, zip_longest
import music21 as mu

class Network():

    """ A network that has a model

    Handles loading and saving different styles for the model
    """

    def __init__(self):

        self.style = 'default'
        self.model = Sequential()

        self.corpus = {'<none>', '<beg>', '<end>' }
        self.timing = {'<none>', '<beg>', '<end>' }
        self.index_to_corpus = {}
        self.corpus_to_index = {}
        self.index_to_timing = {}
        self.timing_to_index = {}


    def load(self, style):
        self.style = style
        self.model.load_weights('%s.h5' % self.style)


    def save(self):
        self.model.save_weights('%s.h5' % self.style)

    def clean(self, note):
        if isinstance(note, mu.chord.Chord):
            note =  mu.chord.Chord(set(note.pitchNames))
            #note = note.pitchedCommonName

        return str(note)

    def train(self, compositions):

        self.corpus |= { self.clean(note) for score in compositions for part in score for note in part }
        self.timing |= { str(note.duration) for score in compositions for part in score for note in part }


        # IDEA add some corpus like walking up the scale or the current chord
        # string repr would look like: '<src.machine.corpus n>'
        # where n is the id of the corpus which we can add to the corpus class

        #print('\n'.join(sorted(corpus)))
        #print('\n'.join(sorted(timing)))

        self.index_to_corpus = dict(enumerate(sorted(self.corpus)))
        self.corpus_to_index = { k:i for i,k in enumerate(sorted(self.corpus)) }

        self.index_to_timing = dict(enumerate(self.timing))
        self.timing_to_index = { k:i for i,k in enumerate(self.timing) }


        self.CORPUS_SIZE = len(self.corpus)
        self.TIMING_SIZE = len(self.timing)
        self.SEQ_LENGTH = 50
        self.HIDDEN_DIM = 50
        self.LAYER_NUM = 2

        self.model = Sequential()
        self.model.add(LSTM(self.HIDDEN_DIM, input_shape=(None, self.CORPUS_SIZE), return_sequences=True))
        for i in range(self.LAYER_NUM-1):
            self.model.add(LSTM(self.HIDDEN_DIM, return_sequences=True))

        self.model.add(TimeDistributed(Dense(self.CORPUS_SIZE)))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

        try:
            self.load(self.style)
        except:
            pass


        for _ in range(1):
            score = compositions[0]

            #data = [ [ [ [ 1 if i is corpus_to_index[str(note)] else 0 for i in range(len(corpus)) ] , [ 1 if i is timing_to_index[str(note.duration)] else 0 for i in range(len(timing)) ] ] for note in part.notesAndRests ] for part in score ]

            # Get the chords notes and rests. However chords should be simple and not contain all pitches. Also we should remove duplicate notes played in sucession as this is more todo with timing
            data = [  self.clean(note) for note in score.parts[0].notesAndRests ]
            #data = filter(lambda x: not re.search('Note|Rest', x), data)
            data = ['<beg>'] + [ x[0] for x in groupby(data) ] + ['<end>']

            # Sequences to train on
            self.NUM_SEQ = 20
            self.SEQ_LENGTH = 1 + len(data) // self.NUM_SEQ

            x_seqs = list(zip_longest( *[iter(data)] * self.NUM_SEQ, fillvalue='<end>'))
            y_seqs = list(zip_longest( *[iter(data[1:])] * self.NUM_SEQ, fillvalue='<end>'))

            x = np.zeros((len(x_seqs), self.SEQ_LENGTH, self.CORPUS_SIZE))
            y = np.zeros((len(y_seqs), self.SEQ_LENGTH, self.CORPUS_SIZE))

            for i in range(len(x_seqs)):
                for j in range(self.SEQ_LENGTH):
                    x[i][j][self.corpus_to_index[ x_seqs[i][j] ] ] = 1
                    y[i][j][self.corpus_to_index[ y_seqs[i][j] ] ] = 1

            #print('\n\n'.join([ ''.join(str(n)) for n in x]))
            self.model.fit(x,y, verbose=0, epochs=200)
            self.save()


    def compose(self, *args):

        ix = [ self.corpus_to_index['<beg>'] ]
        y_char = [ self.index_to_corpus[ix[-1]] ]
        x = np.zeros((1,1000,self.CORPUS_SIZE))

        try:
            for i in range(100):
                x[0,i,:][ix[-1]] = 1
                pred = self.model.predict(x[:, :i+1, :])
                ix = np.argmax(pred[0], 1)
                y_char.append(self.index_to_corpus[ix[-1]])

                print(y_char[-1], end='')
        except KeyboardInterrupt:
            pass


        print('\n'.join(y_char), file=open('output.txt', 'w'))
        print('\n'.join(y_char))
        return y_char




