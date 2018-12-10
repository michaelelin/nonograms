import json
import os
import random

from nonogram import Grid

DATA_DIR = 'data'
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
NONOGRAMS_PATH = os.path.join(DATA_DIR, 'nonograms.json')

class GridData:
    def __init__(self, data_path):
        self.load(data_path)

    def load(self, data_path):
        print('Loading nonograms data...')
        with open(data_path, 'r') as f:
            self._nonograms = json.load(f)
        print('Done')

    def save(self, data_path):
        with open(data_path, 'w') as f:
            json.dump(self._nonograms, f)

    def store(self, nid, grid):
        self._nonograms[nid] = grid.serialize()

    def get(self, nid, **kwargs):
        data = self._nonograms[str(nid)]
        if data:
            return Grid.deserialize(data, nid=nid, **kwargs)
        raise KeyError

    def __iter__(self):
        for nid in self._nonograms:
            yield self.get(nid)

    def __len__(self):
        return len(self._nonograms)

class RandomGridData:
    def __init__(self, size):
        self.size = size

    def get(self, nid, **kwargs):
        random.seed(nid)
        return Grid(self.size, self.size,
                    [[random.randint(0, 1) for _ in xrange(self.size)] for _ in xrange(self.size)],
                    nid)
