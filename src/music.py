#! usr/bin/env python3

class Album():

    def __init__(self, data=None):
        self.compositions = []

    def add(self, composition, args):
        self.compositions.append((composition, args))

    def add(self, args=None):
        return

    def save(self, args=None):
        open(args, 'w').write(str(self))

    def load(self, args=None):
        self.compositions = open(args, 'r').read()

    def __str__(self):
        return '[' + ','.join(self.compositions) + ']'

