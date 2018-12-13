from lxml import html
from tqdm import tqdm
import json
import os
import re
import requests
import sys

from nonograms.data import JsonGridData
from nonograms.nonogram import Grid

DATA_DIR = 'data'
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
NONOGRAMS_PATH = os.path.join(DATA_DIR, 'nonograms.json')

class NonogramDiscovery:
    URL = 'http://www.nonograms.org/nonograms/p/{page}/sort/6'

    def __init__(self):
        self.index = {}

    def discover_all(self):
        page_num = 1
        while self.read_page(page_num):
            page_num += 1
        with open(INDEX_PATH, 'w') as f:
            json.dump(self.index, f)
        print('Wrote index to %s' % INDEX_PATH)

    def read_page(self, page_num):
        print('Reading page %d' % page_num)
        page = requests.get(self.URL.format(page=page_num))
        tree = html.fromstring(page.content)
        descriptions = tree.cssselect('table.nonogram_list > tr > td.nonogram_descr')
        for description in descriptions:
            try:
                nid, params = self.extract_params(description)
                if nid in self.index:
                    return False
                self.index[nid] = params
            except Exception as e:
                print(e)
        return True

    def extract_params(self, description):
        title_el = description.cssselect('.nonogram_title')[0]
        nid = re.match('nonogram_(\d+)', title_el.get('id')).group(1)
        url = title_el.get('href')
        size = description.cssselect('table > tr:nth-child(2) > td:nth-child(2)')[0].text
        match = re.match('(?P<width>\d+)x(?P<height>\d+)', size)
        width = int(match.group('width'))
        height = int(match.group('height'))
        return nid, {
            'width': width,
            'height': height,
            'url': url,
        }

class NonogramDownloader:
    PATTERN = re.compile('^var d=(?P<values>[\d\s,\[\]]+);?$')

    def __init__(self, url):
        self.url = url

    def retrieve(self):
        return self.decode(self.fetch_values())

    def fetch_values(self):
        page = requests.get(self.url)
        tree = html.fromstring(page.content)
        scripts = tree.xpath('//script')
        for script in scripts:
            if script.text:
                match = self.PATTERN.match(script.text.strip())
                if match:
                    # This is relatively safe since match contains only a
                    # limited selection of characters
                    return eval(match.group('values'))
        raise 'Values not found'

    def decode(self, v):
        width = v[1][0] % v[1][3] + v[1][1] % v[1][3] - v[1][2] % v[1][3]
        height = v[2][0] % v[2][3] + v[2][1] % v[2][3] - v[2][2] % v[2][3]
        Aa = v[3][0] % v[3][3] + v[3][1] % v[3][3] - v[3][2] % v[3][3]
        grid = Grid(width, height)

        V = Aa + 5
        Ha = v[V][0] % v[V][3] * (v[V][0] % v[V][3]) + v[V][1] % v[V][3] * 2 + v[V][2] % v[V][3]
        Ia = v[V + 1]

        for u in range(V + 2, V + 1 + Ha + 1):
            for y in range(v[u][0] - Ia[0] - 1, v[u][0] - Ia[0] + v[u][1] - Ia[1] - 1):
                grid[y, v[u][3] - Ia[3] - 1] = v[u][2] - Ia[2]

        return grid

class NonogramSync:
    def __init__(self):
        with open(INDEX_PATH, 'r') as f:
            self.index = json.load(f)
        self.data = JsonGridData()

    def sync(self):
        for nid, props in tqdm(self.index.iteritems(), total=len(self.index)):
            try:
                grid = NonogramDownloader(props['url']).retrieve()
                self.data.store(nid, grid)
            except Exception as e:
                print(e)
        self.data.save(NONOGRAMS_PATH)
        print('Wrote nonograms to %s' % NONOGRAMS_PATH)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'discover':
        NonogramDiscovery().discover_all()
    elif len(sys.argv) > 1 and sys.argv[1] == 'sync':
        NonogramSync().sync()
    else:
        print('Nothing to do')
