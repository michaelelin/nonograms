import sys

from nonograms.data import GridData
from nonograms.view import GuiView
from nonograms.solve import NonogramProblem

if __name__ == '__main__':
    if sys.argv[1] == 'view':
        nid = sys.argv[2]
        data = GridData()
        grid = data.get(nid)
        GuiView(grid)
    elif sys.argv[1] == 'solve':
        nid = sys.argv[2]
        data = GridData()
        grid = data.get(nid)
        grid.clear()
        problem = NonogramProblem(grid)
        GuiView(grid)
    else:
        print('Nothing to do')


