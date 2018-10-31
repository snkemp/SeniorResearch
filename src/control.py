"""
"""

import json

import datetime as D

from src.machine import Network
from src.music import Collection

class Manager():

    """ Manages musicians and machines

    """

    def __init__(self, args):
        """ Create a network to handle machine learning and a collection to handle musical data """

        self.args = args
        self.network = Network()
        self.collection = Collection()

        try:
            self.init()
        except:
            print('Something went wrong when initializing, nothing was done')
            pass


    def execute(self, *args):
        print(args)


    def make(self, *args):
        self.init()
        self.load()
        self.train()
        self.compose()
        self.save()

    def create(self, style='toh-kay', *args):
        """ Create files for us to store data in, note this will overwrite data """
        style = style.lower()
        self.verbose('Creating %s...' % style)

        network = open('%s.h5' % style, 'x+')
        network.write('')
        network.close()

        collection = open('%s.json' % style, 'x+')
        collection.write('{}')
        collection.close()

        try:  # We expect this to fail, however it is important our manager knows what style to save so we can save it again later
            self.load(style)
        except Exception as e:
            print(e)

        self.save()



    def init(self, style='toh-kay', *args):
        """ Have our network and collection load the given style """
        style = style.lower()
        self.verbose('Initializing %s...' % style)

        self.collection.load(style)
        self.network.init(self.collection)


    def load(self, *args):
        self.verbose('Loading weights...')
        self.network.load()


    def save(self):
        """ Have our network and collection save their progress """
        self.verbose('Saving...')
        self.collection.save()
        self.network.save()



    def train(self):
        """ Train the network on the compositions """
        self.verbose('Training...')
        self.network.train()


    def compose(self):
        """ Compose """
        self.verbose('Composing...')
        self.network.compose()



    def print(self):
        self.verbose('Printing...')
        with open('debug/concepts/%s.txt'%self.network.style, 'w') as f:
            print( D.datetime.now().strftime('%d %b %H:%M') + ('#'*80).join( map(str, self.network.opus) ), file=f )


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


