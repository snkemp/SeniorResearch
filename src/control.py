"""
"""

import os, json, glob
import datetime as D

from music21.midi import MidiFile
from music21.midi.translate import streamToMidiFile, midiFileToStream

from src.machine import Network
from src.music import Artist

class Manager():

    """ Manages musicians and machines

    """

    def __init__(self, args):
        """ Create a network to handle machine learning and a collection to handle musical data """

        self.args = args
        self.network = Network()
        self.artist = Artist()


    def execute(self, *args):
        """ Execute python script of args """
        # TODO
        print(args)


    def make(self, *args):
        self.load()
        self.compose()
        self.save()

    def create(self, style='toh-kay', *args):
        """ Create files for us to store data in, note this might overwrite data """
        style = style.lower()
        self.verbose('Creating %s...' % style)

        network = open('%s.h5' % style, 'x+')
        network.write('')
        network.close()

        collection = open('%s.json' % style, 'x+')
        collection.write('{}')
        collection.close()

        try:  # We expect this to fail, however it is important our manager knows what style to save so we can save it again later
            self.init(style)
        except Exception as e:
            print(e)

        self.save()



    def init(self, style='toh-kay', *args):
        """ Have our network load and parse data associated with the given style """
        self.style = style.lower()
        self.verbose('Initializing %s...' % self.style)

        self.network.init(self.style)
        self.artist.init(self.style)

    def load(self, style='toh-kay', *args):
        """ Load previously saved data with respect to the given style """
        self.style = style.lower()
        self.verbose('Loading %s...' % self.style)

        self.network.load(self.style)
        self.artist.load(self.style)


    def save(self, *args):
        """ Save network progress and all compositions """
        self.verbose('Saving...')

        self.network.save()
        self.artist.save()


    def train(self, n=1, *args):
        """ Train the network on the compositions n amount of times """
        self.verbose('Training...')
        training_data = self.artist.training_data
        for i in range(int(n)):
            self.verbose('Session %4d' % i)
            self.network.train(training_data)


    def compose(self, n=1, *args):
        """ Compose """
        self.verbose('Composing...')
        for i in range(int(n)):
            self.verbose('Composition %4d:' % i)
            data = self.artist.compose(self.network)
            self.verbose('\tKey: %s\n\tScale: %s\n\tProgression: %s\n\tNotes: %s' % data)



    def print(self, *args):
        """ Internal use for debug purposes """
        self.verbose('Printing...')
        print(*args)


    def quit(self, *args):
        """ For user and internal use. Quit """
        raise StopIteration


    def exit(self, msg='', *args):
        """ For internal use only, quit after printing some kind of message """
        print(msg)
        self.quit()


    def verbose(self, *args):
        """ Print a message if user wants us to print helpful status messages """
        isdict = isinstance(self.args, dict)
        if (isdict and self.args['verbose']) or (not isdict and self.args.verbose):
            for msg in args:
                print(msg)


    def error(self, msg, *args):
        print('Error: %s' % msg)
        if args:
            print(*args)


