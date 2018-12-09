class Grid:
    def __init__(self, width, height, grid=None, nid=None):
        self.nid = nid
        self.width = width
        self.height = height
        self.grid = grid or [[0] * width for _ in xrange(height)]
        self.rows = [self._project_line(self.grid[y])
                     for y in xrange(height)]
        self.columns = [self._project_line([row[x] for row in self.grid])
                        for x in xrange(width)]
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def clear(self):
        for y in xrange(self.height):
            for x in xrange(self.width):
                self[x,y] = None

    def _project_line(self, line):
        lengths = []
        cell_count = 0
        for cell in line:
            if cell == 1:
                cell_count += 1
            elif cell_count > 0:
                lengths.append(cell_count)
                cell_count = 0
        if cell_count > 0:
            lengths.append(cell_count)
        return lengths

    def serialize(self):
        return {
            'id': self.nid,
            'width': self.width,
            'height': self.height,
            'grid': self.grid,
        }

    @staticmethod
    def deserialize(data, **kwargs):
        return Grid(
            data['width'],
            data['height'],
            data['grid'],
            data['id'],
            **kwargs
        )

    def __getitem__(self, (x,y)):
        return self.grid[y][x]

    def __setitem__(self, (x,y), val):
        self.grid[y][x] = val

    def __str__(self):
        lines = []
        for row in self.grid:
            lines.append(''.join(['#' if cell else '-' for cell in row]))
        return '\n'.join(lines)

