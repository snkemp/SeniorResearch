#! usr/bin/env/ python3

import os, re, sys
from argparse import ArgumentParser

from machine import Network
from music import Album

class Interpreter(ArgumentParser):

    WELCOME = '\n\t\t---  MuGen  ---\n'
    GOODBYE = '\nEnd -'

    ALBUM = 'album.json'
    NETWORK = 'network.h5'


    def __init__(self, args):
        super().__init__()

        self.args = args
        if self.args.verbose:
            print(Interpreter.WELCOME)

        self.add_argument('command')

        # compose
        self.add_argument('--key', '-k', nargs=1, default='C')
        self.add_argument('--count', '-c', nargs=1, default='1')
        self.add_argument('--style', '-s', nargs=1, default='toh-kay')
        self.add_argument('args', nargs='*', default='')

        self.album = Album()
        self.network = Network()

    def __iter__(self):
        return self


    def __next__(self):
        print('>', end=' ')
        command = input()
        if re.match('exit|quit|q|Q', command):
            raise StopIteration
        self.execute(command)
        return self


    def execute(self, command):
        command = self.parse_args(command.split(' '))

        if self.args.verbose:
            print(command)

        try:  # get function by name and call it
            func =  getattr(self, command.command)
            func(command.args)

        except AttributeError:
            print('No command matches ' + command.command)
        except:
            print('Something went wrong, nothing was done')
            raise


    def save(self, args=None):
        if self.album:
            self.album.save(os.path.join(self.args.output, Interpreter.ALBUM))
            if self.args.verbose:
                print('Saved compositions')


        if self.network:
            self.network.save(os.path.join(self.args.output, Interpreter.NETWORK))
            if self.args.verbose:
                print('Saved network model weights')


    def load(self, args=None):
        self.album.load(os.path.join(self.args.output, Interpreter.ALBUM))
        if self.args.verbose:
            print('Loaded compositions')

        self.network.load(os.path.join(self.args.output, Interpreter.NETWORK))
        if self.args.verbose:
            print('Loaded trained network')


    def compose(self, args=None):

        self.album.add(self.convert(self.network.compose(self.args)))
        if self.args.verbose:
            print('Composition written and added to album')


    def train(self, args=None):

        self.network.train(self.args)
        if self.args.verbose:
            print('Network trained on data')


    def print(self, args='Nothing to print'):
        print(args)

    def exit(self, msg=None):
        if self.args.verbose:
            print(msg or Interpreter.GOODBYE)

        sys.exit(0)

