"""
"""

import re, json

import numpy as np
#np.random.seed(73)

from keras.models import Sequential, load_model
from keras.layers import Input, Dense, Activation, LSTM, TimeDistributed, Flatten, Reshape, Dropout, Embedding
from keras.callbacks import ModelCheckpoint

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.utils import to_categorical

from itertools import groupby, zip_longest

import music21 as mu

import json



class Network():

    """ A network that has a model

    Handles loading and saving different styles for the model
    """

    def __init__(self):
        pass

    def init(self, artist):
        notes = artist.notes

        seq_len = 100

        int_to_note = sorted(set(notes))
        note_to_int = { k: i for i,k in enumerate(int_to_note)}

        num_notes = len(int_to_note)

        x = []
        y = []

        for i in range(len(notes) - seq_len):
            xseq = notes[i:i+seq_len]
            yseq = notes[i+seq_len]

            x.append([ note_to_int[n] for n in xseq])
            y.append(note_to_int[yseq])


        n_patterns = len(x)

        self.x = np.reshape(x, (n_patterns, seq_len, 1)) #/ num_notes
        self.y = to_categorical(y)

        self.model = Sequential()
        self.model.add(LSTM(512, input_shape=(self.x.shape[1],self.x.shape[2]), return_sequences=True))
        self.model.add(Dropout(.2))
        self.model.add(LSTM(512, return_sequences=True))
        self.model.add(Dropout(.3))
        self.model.add(LSTM(512))
        self.model.add(Dense(256))
        self.model.add(Dropout(.2))
        self.model.add(Dense(num_notes))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

        self.int_to_note = int_to_note
        self.note_to_int = note_to_int


    def train(self, e=20, b=64, *args):
        self.model.fit(self.x, self.y, epochs=int(e), batch_size=int(b), verbose=1)
        self.save()

    def predict(self, sequence):
        start = self.note_to_int['START']

        Z = np.array([start for _ in range(100)]).reshape((1,100,1))
        Z[0, -len(sequence):, 0] = [ self.note_to_int[str(s)] for s in sequence ]

        prediction = self.model.predict(Z)
        y = np.argmax(prediction)
        if self.int_to_note[y] == sequence[-1]:
            prediction[0][y] = 0
            y = np.argmax(prediction)
        return self.int_to_note[np.argmax(prediction)]

    def save(self, s='toh-kay'):
        self.model.save('%s.h5' % s)
        data = { 'encode': self.note_to_int, 'decode': self.int_to_note }
        with open('data.%s.json' % s, 'w') as f:
            json.dump(data, f)

    def load(self, s='toh-kay'):
        self.model = load_model('%s.h5' % s)
        with open('data.%s.json' % s, 'r') as f:
            data = json.load(f)
            self.note_to_int = data['encode']
            self.int_to_note = data['decode']


