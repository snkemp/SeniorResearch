"""
"""

import re, json

import numpy as np
#np.random.seed(73)

from keras.models import Sequential, model_from_json
from keras.layers import Input, Dense, Activation, LSTM, TimeDistributed, Flatten, Reshape, Dropout
from keras.callbacks import ModelCheckpoint

from itertools import groupby, zip_longest
import music21 as mu

from src.concepts import encode, decode, START, STOP

class Network():

    """ A network that has a model

    Handles loading and saving different styles for the model
    """

    def __init__(self, style='default'):
        self.style = style

        HIDDEN_DIM = 500
        LAYER_NUM = 3
        NUM_NOTES = 15  # 12 notes, Rest, START, END

        self.melody = Sequential()
        self.melody.add(LSTM(HIDDEN_DIM, input_shape=(None, NUM_NOTES), return_sequences=True))
        self.melody.add(Activation('softmax'))
        self.melody.add(Dense(NUM_NOTES))

        self.melody.compile(loss='categorical_crossentropy', optimizer='adam')


        filepath= style + "-melody-{epoch:02d}-{loss:.4f}.hdf5"
        checkpoint=ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
        self.callbacks = [checkpoint]

        # TODO Harmony
        self.harmony = Sequential()


    def init(self, *args):
        self.__init__(*args)



    def save(self):
        self.melody.save_weights('%s.melody.h5' % self.style)
        self.harmony.save_weights('%s.harmony.h5' % self.style)


    def load(self, style):
        self.style = style

        try:
            self.melody.load_weights('%s.melody.h5' % self.style)
            self.harmony.load_weights('%s.harmony.h5' % self.style)
        except:
            print('There was a problem loading the model weights.')



    def prepare(self):
        ...

    def train(self, td):
        for x,y in td:
            self.melody.fit(x, y, batch_size=10, verbose=1, epochs=10, callbacks=self.callbacks )
            self.save()


    def predict(self, starting_note, n):

        ix = [ encode(START) ]
        x = np.zeros((1, n, 15))

        for i in range(n):
            x[0, i, :][ix[-1]] = 1

            pred = self.melody.predict(x[:, :i+1, :])
            ix.append(np.argmax(pred))
            if ix[-1] == encode(STOP):
                break

        melody = ix
        return melody
