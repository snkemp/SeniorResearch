"""
"""

import re, json

import numpy as np
np.random.seed(73)

from keras.models import Sequential, model_from_json
from keras.layers import Input, Dense, Activation, LSTM, TimeDistributed, Flatten, Reshape


from itertools import groupby, zip_longest
import music21 as mu

from src.concepts import Opus
from src.music import Composition


class Network():

    """ A network that has a model

    Handles loading and saving different styles for the model
    """

    def __init__(self, style='default'):
        self.style = style


    def save(self):
        with open('data/%s/opus.json' % self.style, 'w') as f:
            f.write(self.opus.toJSON())

        self.melody.save_weights('%s.melody.h5' % self.style)
        self.harmony.save_weights('%s.harmony.h5' % self.style)


    def init(self, collection):
        self.opus = Opus(collection)
        self.prepare()


    def prepare(self):
        HIDDEN_DIM = 500
        LAYER_NUM = 2

        self.melody = Sequential()
        self.melody.add(LSTM(HIDDEN_DIM, input_shape=(None, self.opus.numNotes), return_sequences=True))
        for _ in range(LAYER_NUM):
            self.melody.add(LSTM(HIDDEN_DIM, return_sequences=True))
        self.melody.add(TimeDistributed(Dense(self.opus.numNotes)))
        self.melody.add(Activation('softmax'))
        self.melody.compile(loss='categorical_crossentropy', optimizer='rmsprop')

        # TODO Harmony
        self.harmony = Sequential()

    def load(self, style):
        self.style = style

        with open('data/%s/opus.json' % self.style, 'r') as f:
            self.opus = Opus([])
            self.opus.fromJSON(f.read())

        self.prepare()

        try:
            self.melody.load_weights('%s.melody.h5' % self.style)
            self.harmony.load_weights('%s.harmony.h5' % self.style)
        except:
            print('There was a problem loading the model weights.')


    def train(self, *args):

        SEQ_LENGTH = 50

        for melody in self.opus.melodies:
            data = [ pitches[0].pitchClass for pitches in melody ]
            if len(data) == 0:
                continue

            x = np.zeros((len(melody)//SEQ_LENGTH, SEQ_LENGTH, self.opus.numNotes))
            y = np.zeros((len(melody)//SEQ_LENGTH, SEQ_LENGTH, self.opus.numNotes))

            for i in range(len(melody)//SEQ_LENGTH):
                x_seq = data[i*SEQ_LENGTH : (i+1)*SEQ_LENGTH]
                x_seq_ix = [ self.opus.note_to_index[ note ] for note in x_seq ]

                y_seq = data[i*SEQ_LENGTH+1 : (i+1)*SEQ_LENGTH + 1]
                y_seq_ix = [ self.opus.note_to_index[ note ] for note in y_seq ]

                ip_seq = np.zeros((SEQ_LENGTH, self.opus.numNotes))
                tg_seq = np.zeros((SEQ_LENGTH, self.opus.numNotes))

                for j in range(SEQ_LENGTH):
                    ip_seq[j][ x_seq_ix[j] ] = 1
                    tg_seq[j][ y_seq_ix[j] ] = 1

                x[i] = ip_seq
                y[i] = tg_seq

            self.melody.fit(x, y, batch_size=50, verbose=1, epochs=20)

        self.save()


    def generateMelody(self, harmony, melody):
        ix = []
        x = np.zeros((len(harmony),50,self.opus.numNotes))

        for i,chord in enumerate(harmony):
            ix.append(harmony.randomStartingNote(chord))
            for j in range(50):
                x[i, j, :][ix[-1]] = 1
                pred = self.melody.predict(x[:, :j+1, :])[0]

                next_prediction = pred[0]
                sum_probabilities = sum(next_prediction)

                rand_value = np.random.choice(next_prediction, p=[ _p/sum_probabilities for _p in next_prediction ])
                jx = np.where(next_prediction == rand_value)
                ix.append(jx[0][0])

        y = [ self.opus.index_to_note[ix_k] for ix_k in ix ]
        return y

    def compose(self, length=50, n=1, *args):
        composition = Composition()
        return [ composition.compose(self) for _ in range(int(n)) ]




