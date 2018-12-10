import time
import traceback

from nonogram import Grid
from util import Direction, InconsistencyException, TimeoutException
from line_solver import LineSolver

class NonogramProblem:
    def __init__(self, grid):
        self.grid = grid
        grid.set_controller(self)
        self.cells = [[Cell(self, x, y) for x in xrange(grid.width)]
                      for y in xrange(grid.height)]
        self.constraints = list(reversed(
            [LineConstraint(self, proj, cells,
                            direction=Direction.ROW,
                            coord=i)
             for i, (proj, cells) in enumerate(zip(grid.rows, self.cells))] +
            [LineConstraint(self, proj, [row[i] for row in self.cells],
                            direction=Direction.COLUMN,
                            coord=i)
             for i, proj in enumerate(grid.columns)]
        ))

        self.dirty_constraints = self.constraints[:]
        self.state_stack = [] # Used for backtracking

    def next_constraint(self):
        return self.dirty_constraints and self.dirty_constraints[-1]

    def solve(self, abort_time=None):
        while self.step():
            if abort_time and time.clock() > abort_time:
                raise TimeoutException()

    def step(self, debug=False):
        if not self.dirty_constraints:
            blank_cells = self.blank_cells()
            if blank_cells:
                self.branch(blank_cells)
                return True
            else:
                return False

        constraint = self.dirty_constraints.pop()
        try:
            constraint.step(debug)
        except InconsistencyException:
            self.backtrack()
        return True

    def branch(self, blank_cells):
        cell, value = self.choose_branch(blank_cells)
        if value:
            cell.fill()
        else:
            cell.cross()
        self.state_stack.append(self.freeze_state(cell))

    def choose_branch(self, blank_cells):
        return blank_cells[0], True

    def freeze_state(self, branch_cell):
        return {
            'branch_cell': branch_cell,
            'state': [[cell.state for cell in row] for row in self.cells],
        }

    def backtrack(self):
        if not self.state_stack:
            raise InconsistencyException()
        last_state = self.state_stack.pop()
        self.restore_and_toggle(last_state)

    def restore_and_toggle(self, state):
        while self.dirty_constraints:
            self.dirty_constraints.pop().dirty = False
        for row, frozen_row in zip(self.cells, state['state']):
            for cell, frozen_state in zip(row, frozen_row):
                cell.state = frozen_state
                if frozen_state == True:
                    self.grid[cell.x,cell.y] = 1
                elif frozen_state == False:
                    self.grid[cell.x,cell.y] = 0
                else:
                    self.grid[cell.x,cell.y] = None
        if state['branch_cell'].state:
            state['branch_cell'].cross()
        else:
            state['branch_cell'].fill()


    def mark_dirty(self, constraint):
        self.dirty_constraints.insert(0, constraint)

    def blank_cells(self):
        cells = []
        for row in self.cells:
            for cell in row:
                if cell.state is None:
                    cells.append(cell)
        return cells

class Cell:
    def __init__(self, problem, x, y):
        self.problem = problem
        self.x = x
        self.y = y
        self.constraints = {}
        self.state = None

    def fill(self, direction=None):
        if self.state != True:
            self.mark_dirty(direction)
        self.state = True
        self.problem.grid[self.x,self.y] = 1

    def cross(self, direction=None):
        if self.state != False:
            self.mark_dirty(direction)
        self.state = False
        self.problem.grid[self.x,self.y] = 0

    def mark_dirty(self, direction=None):
        for d, constraint in self.constraints.iteritems():
            if d != direction:
                constraint.mark_dirty()

    def add_constraint(self, constraint, direction):
        self.constraints[direction] = constraint

    def __nonzero__(self):
        return bool(self.state)

class LineConstraint:
    def __init__(self, problem, proj, cells, direction, coord):
        self.problem = problem
        self.proj = proj
        self.width = len(cells)
        self.cells = cells
        self.direction = direction
        self.coord = coord
        for cell in self.cells:
            cell.add_constraint(self, direction)
        self.dirty = True

    def step(self, debug=False):
        if debug:
            import ipdb; ipdb.set_trace()
        self.dirty = False
        self.constrain()

    def constrain(self):
        solver = LineSolver(self.cells, self.direction)
        solver.solve(self.proj)

    def mark_dirty(self):
        if not self.dirty:
            self.dirty = True
            self.problem.mark_dirty(self)



# TODO Could cache the index of the run a cell belongs to in the cell object


