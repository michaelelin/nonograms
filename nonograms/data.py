import json
import os
import random
from xml.etree import ElementTree

from nonogram import Grid

DATA_DIR = 'data'
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
NONOGRAMS_PATH = os.path.join(DATA_DIR, 'nonograms.json')


class GridData:
    def get(self, nid, **kwargs):
        raise NotImplemented

    def __iter__(self):
        for nid in self._nonograms:
            yield self.get(nid)

    def __len__(self):
        return len(self._nonograms)

    @staticmethod
    def load(filename):
        print('Loading nonograms data...')
        if filename.endswith('.json'):
            data = JsonGridData(filename)
        elif filename.endswith('.xml'):
            data = XmlGridData(filename)
        else:
            raise ValueError('Unspecified file format')
        print('Done')
        return data


class JsonGridData(GridData):
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self._nonograms = json.load(f)

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


class XmlGridData(GridData):
    CHAR_MAP = { 'X': 1, '.': 0 }
    def __init__(self, filename):
        tree = ElementTree.parse(filename)
        puzzle_node = tree.getroot().find('puzzle')
        solution_text = puzzle_node.find('solution').find('image').text
        solution_lines = [line.strip(' |') for line in solution_text.strip().split('\n')]
        self.nid = puzzle_node.find('id').text
        self.solution = [[XmlGridData.CHAR_MAP[c] for c in line] for line in solution_lines]
        self.width = len(self.solution[0])
        self.height = len(self.solution)

    def get(self, nid, **kwargs):
        return Grid(self.width, self.height, grid=self.solution, nid=self.nid)


class RandomGridData(GridData):
    def __init__(self, size):
        self.size = size

    def get(self, nid, **kwargs):
        random.seed(nid)
        return Grid(self.size, self.size,
                    [[random.randint(0, 1) for _ in xrange(self.size)] for _ in xrange(self.size)],
                    nid=nid)
