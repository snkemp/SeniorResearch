"""
"""

import re, json

import numpy as np
np.random.seed(73)

from keras.models import Sequential, model_from_json
from keras.layers import Input, Dense, Activation, LSTM, TimeDistributed, Flatten


from itertools import groupby, zip_longest
import music21 as mu

from src.concepts import conceptualize, Concept

class Network():

    """ A network that has a model

    Handles loading and saving different styles for the model
    """

    def __init__(self, style='default'):

        self.style = style
        self.model = Sequential()

        self.corpus = { Concept.NONE, Concept.BEGINNING, Concept.END }
        self.index_to_corpus = {}
        self.corpus_to_index = {}

    def save(self):
        self.model.save_weights('%s.h5' % self.style)


    def init(self, collection):
        self.style = collection.style

        self.opus = conceptualize(collection.compositions())

        self.corpus.update(*[ composition.corpus for composition in self.opus ])

        self.index_to_corpus = dict(enumerate(sorted(self.corpus)))
        self.corpus_to_index = { k:i for i,k in self.index_to_corpus.items() }

        self.CORPUS_SIZE = len(self.corpus)
        self.SEQ_LENGTH = 20
        self.HIDDEN_DIM = 20
        self.LAYER_NUM = 4

        self.model = Sequential()
        self.model.add(LSTM(self.HIDDEN_DIM, input_shape=(None, self.CORPUS_SIZE), return_sequences=True))
        for i in range(self.LAYER_NUM-1):
            self.model.add(LSTM(self.HIDDEN_DIM, return_sequences=True))

        self.model.add(TimeDistributed(Dense(self.CORPUS_SIZE)))
        self.model.add(Activation('softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')


    def load(self):
        try:
            self.model.load_weights('%s.h5' % self.style)
        except:
            print('Could not load weights. Retraining and saving weights')
            self.train()



    def train(self, *args):

        for composition in self.opus:

            data = composition.data

            # Sequences to train on
            self.SEQ_LENGTH = 20
            self.NUM_SEQ = len(data) // self.SEQ_LENGTH

            x_seqs = list(zip_longest( *[iter(data)] * self.NUM_SEQ, fillvalue=Concept.NONE))
            y_seqs = list(zip_longest( *[iter(data[1:])] * self.NUM_SEQ, fillvalue=Concept.NONE))

            x = np.zeros((len(x_seqs), self.SEQ_LENGTH, self.CORPUS_SIZE))
            y = np.zeros((len(y_seqs), self.SEQ_LENGTH, self.CORPUS_SIZE))

            for i in range(len(x_seqs)):
                for j in range(self.SEQ_LENGTH):
                    x[i][j][ self.corpus_to_index[ x_seqs[i][j] ] ] = 1
                    y[i][j][ self.corpus_to_index[ y_seqs[i][j] ] ] = 1

            print('Data is ready. Fitting to model...')
            self.model.fit(x,y, verbose=0, epochs=100)
            self.save()


    def compose(self, *args):

        ix = [ self.corpus_to_index[Concept.BEGINNING] ]
        y_char = [ self.index_to_corpus[ix[-1]] ]
        x = np.zeros((1,self.SEQ_LENGTH,self.CORPUS_SIZE))

        try:
            for i in range(self.SEQ_LENGTH):
                x[0,i,:][ix[-1]] = 1
                pred = self.model.predict(x[:, :i+1, :])[0]
                print(pred)
                ix = np.argmax(pred, 1)
                y_char.append(self.index_to_corpus[ix[-1]])

                print(y_char[-1], end='')
        except KeyboardInterrupt:
            pass


        print('\n'.join(map(repr, y_char)), file=open('output.txt', 'w'))
        print('\n'.join(map(repr, y_char)) )
        return y_char

