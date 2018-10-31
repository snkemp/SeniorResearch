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

        data = [ concept for composition in self.opus for field in composition for concept in field ]
        x = np.zeroes((len(data)//self.SEQ_LENGTH, self.SEQ_LENGTH, len(self.corpus)))
        y = np.zeroes((len(data)//self.SEQ_LENGTH, len(self.corpus)))

        for i in range(0, len(data) - self.SEQ_LENGTH):
            x_seq = data[i: i+self.SEQ_LENGTH]
            y_seq = data[i+self.SEQ_LENGTH]

            x_seq_ix = [ self.corpus_to_index[d] for d in x_seq ]
            y_seq_ix = self.corpus_to_index[y_seq]

            for j, ix in enumerate(x_seq_ix):
                x[i][j][ix] = 1

            y[i][ y_seq_ix ] = 1


        self.model.fit(x, y, verbose=1, epochs=100)
        self.save()


    def compose(self, *args):

        composition = [ Concept.BEGINNING ]
        for i in range(100):

            ix =

