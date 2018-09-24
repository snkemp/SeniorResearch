

from keras.models import Sequential
from keras.layers import Dense, Activation, LSTM

import numpy as np

class Network():

    def __init__(self, data=None):
        np.random.seed(7)
        self.model = Sequential([
                Dense(32, input_shape=(12,)),
                Activation('relu'),
                Dense(12, activation='sigmoid'),
                Activation('softmax')
            ])

        self.model.compile(optimizer='rmsprop',
                           loss='categorical_crossentropy',
                           metrics=['accuracy'])


    def load(self, filename):
        self.model.load_weights(filename)

    def save(self, filename):
        self.model.save_weights(filename)

    def train(self, args):

        data = np.random.random((12,12))
        labels = np.random.randint(2, size=(12,12))

        self.model.fit(data, labels, epochs=10, batch_size=10)


    def compose(self, args=None):

        return model.predict(np.random.random(100,1))


