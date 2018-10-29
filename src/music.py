"""
"""

import os, json, glob
import music21 as mu

class Collection():

    """ A collection of music
    """

    def __init__(self):
        """ Initialize
        """

        self.album = {}
        self.style = 'default'

    def load(self, style):
        self.style = style
        self.album = json.load(open('%s.json' % self.style, 'r'))

    def save(self):
        json.dump(self.album, open('%s.json' % self.style, 'w'))

    def compositions(self):
        files = glob.glob('data/%s/*.mid' % self.style)

        scores = []
        for f in files:
            sc = mu.converter.parse(f)
            print([part.partName for part in sc.parts])
            score = mu.stream.Score([ part for part in sc.parts if part.partName in ('Guitar', 'Voice', None) ])
            scores.append(score)

        return scores


    def add(self, score):
        pass
