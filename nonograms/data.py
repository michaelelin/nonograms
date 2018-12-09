import json
import os

from nonogram import Grid

DATA_DIR = 'data'
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
NONOGRAMS_PATH = os.path.join(DATA_DIR, 'nonograms.json')

class GridData:
    def __init__(self):
        self.load()

    def load(self):
        print('Loading nonograms data...')
        with open(NONOGRAMS_PATH, 'r') as f:
            self._nonograms = json.load(f)
        print('Done')

    def save(self):
        with open(NONOGRAMS_PATH, 'w') as f:
            json.dump(self._nonograms, f)

    def store(self, nid, grid):
        self._nonograms[nid] = grid.serialize()

    def get(self, nid, **kwargs):
        data = self._nonograms[nid]
        if data:
            return Grid.deserialize(data, **kwargs)
        raise KeyError

    def __iter__(self):
        for nid in self._nonograms:
            yield self.get(nid)
