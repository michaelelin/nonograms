import Tkinter as tk

from nonogram import Grid
from util import Direction

CELL_SIZE = 12
CLUE_SIZE = 10
COLORS = {
    None: '#ffffff',
    0: '#ffcccc',
    1: '#000000',
}
HIGHLIGHT_COLOR = '#ffff99'

class NonogramCell:
    def __init__(self, parent, x, y, color=None):
        self.parent = parent
        self.x = x
        self.y = y
        self.color = color
        self.id = parent.create_rectangle(
                x*CELL_SIZE,
                y*CELL_SIZE,
                x*CELL_SIZE+CELL_SIZE,
                y*CELL_SIZE+CELL_SIZE,
                fill=color, outline='')

    def set_color(self, color):
        if color != self.color:
            self.color = color
            self.parent.itemconfig(self.id, fill=color)

class NonogramClue:
    def __init__(self, parent, proj, direction, coord):
        self.parent = parent
        self.proj = proj
        self.direction = direction
        self.coord = coord
        self.span_ids = [self._draw_span(i, span) for i, span in enumerate(reversed(proj))]

    def _draw_span(self, index, span):
        if self.direction == Direction.ROW:
            x = self.parent.proj_width - index - 0.5
            y = self.parent.proj_height + self.coord + 0.5
        else:
            x = self.parent.proj_width + self.coord + 0.5
            y = self.parent.proj_height - index - 0.5
        self.parent.create_text(
            CELL_SIZE * x,
            CELL_SIZE * y,
            text=span,
            font=('Courier Bold', CLUE_SIZE),
        )

class ClueHighlight:
    def __init__(self, parent):
        self.parent = parent
        self.id = None

    def move(self, constraint):
        if not constraint:
            if self.id:
                self.parent.delete(self.id)
                self.id = None
        elif self.id is None:
            self.id = self.parent.create_rectangle(
                *self.coords(constraint),
                fill=HIGHLIGHT_COLOR, outline=''
            )
            self.parent.tag_lower(self.id)
        else:
            self.parent.coords(self.id, *self.coords(constraint))

    def coords(self, constraint):
        if constraint.direction == Direction.ROW:
            return (
                0,
                (self.parent.proj_height + constraint.coord) * CELL_SIZE,
                (self.parent.proj_width + self.parent.grid.width) * CELL_SIZE,
                (self.parent.proj_height + constraint.coord + 1) * CELL_SIZE,
            )
        elif constraint.direction == Direction.COLUMN:
            return (
                (self.parent.proj_width + constraint.coord) * CELL_SIZE,
                0,
                (self.parent.proj_width + constraint.coord + 1) * CELL_SIZE,
                (self.parent.proj_height + self.parent.grid.height) * CELL_SIZE,
            )


class NonogramCanvas(tk.Canvas):
    def __init__(self, parent, grid):
        self.grid = grid
        self.proj_width = max(len(proj) for proj in grid.rows)
        self.proj_height = max(len(proj) for proj in grid.columns)
        tk.Canvas.__init__(self,
                parent,
                width=(grid.width + self.proj_width) * CELL_SIZE,
                height=(grid.height + self.proj_height) * CELL_SIZE,
                )

        self.clue_highlight = ClueHighlight(self)
        self.highlight_next_line()

        self.proj_rows = [NonogramClue(self, proj, Direction.ROW, y)
                          for y, proj in enumerate(grid.rows)]
        self.proj_cols = [NonogramClue(self, proj, Direction.COLUMN, x)
                          for x, proj in enumerate(grid.columns)]
        self.cells = [[NonogramCell(self, x+self.proj_width, y+self.proj_height, COLORS[grid[x,y]])
                       for x in range(grid.width)]
                      for y in range(grid.height)]
        self._draw_grid()

    def redraw(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.cells[y][x].set_color(COLORS[self.grid[x,y]])
        self.highlight_next_line()

    def highlight_next_line(self):
        if self.grid.controller:
            self.clue_highlight.move(self.grid.controller.next_constraint())

    def _draw_grid(self):
        for x in xrange(self.grid.width + 1):
            self.create_line(
                CELL_SIZE * (self.proj_width + x),
                0,
                CELL_SIZE * (self.proj_width + x),
                CELL_SIZE * (self.proj_height + self.grid.height),
                width=(2 if x % 5 == 0 else 1),
            )
        for y in xrange(self.grid.height + 1):
            self.create_line(
                0,
                CELL_SIZE * (self.proj_height + y),
                CELL_SIZE * (self.proj_width + self.grid.width),
                CELL_SIZE * (self.proj_height + y),
                width=(2 if y % 5 == 0 else 1),
            )

class GuiView:
    def __init__(self, grid):
        self.root = tk.Tk()
        self.app = tk.Frame(self.root)
        self.grid = grid

        self.canvas = NonogramCanvas(self.app, grid)
        self.canvas.pack(side='left', fill=tk.BOTH, expand=1)

        if grid.controller:
            self.controls = tk.Frame(self.app)
            self.controls.pack(side='right')
            self.btn_solve = tk.Button(self.controls, text='Solve', command=self.solve)
            self.btn_solve.pack()
            self.btn_pause = tk.Button(self.controls, text='Pause', command=self.pause)
            self.btn_pause.pack()
            self.btn_step = tk.Button(self.controls, text='Step', command=self.step)
            self.btn_step.pack()
            self.btn_debug_step = tk.Button(self.controls, text='Debug', command=lambda: self.step(True))
            self.btn_debug_step.pack()

        self.app.pack(side='top', fill='both', expand=True)
        self.root.mainloop()

    def solve(self):
        self._paused = False
        self._solve()

    def _solve(self):
        if (not self._paused) and self.grid.controller.step():
            self.canvas.redraw()
            self.root.after(10, self._solve)

    def pause(self):
        self._paused = True

    def step(self, debug=False):
        if self.grid.controller.step(debug):
            self.canvas.redraw()
        else:
            self.root.destroy()

    def debug_step(self):
        self.step(True)
