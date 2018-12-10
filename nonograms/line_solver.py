from util import InconsistencyException

# TODO
# - Some cells can be filled even if they don't belong to the leftmost and
#   rightmost placements of a single run
# 3 3 1   ----- | -##-#----
# 5 1 1 2 ##### | --#------
# - Mark each run with the spans it may belong to
# - Can we mark each (filled/unfilled) cell with the runs it may belong to?
class LineSolver:
    def __init__(self, cells, direction):
        self.cells = cells
        self.direction = direction
        self.spans = CellSpan.split(cells)

    def solve(self, runs):
        if not runs:
            for cell in self.cells:
                cell.cross(self.direction)
            return

        left_sol = self.solve_left(runs)
        right_sol = self.solve_right(runs)
        for run, left, right in zip(runs, left_sol, right_sol):
            for i in xrange(right, left + run):
                self.cells[i].fill(self.direction)

        for run, right, left in zip(runs, right_sol, left_sol[1:]):
            for i in xrange(right + run, left):
                self.cells[i].cross(self.direction)

        for i in xrange(left_sol[0]):
            self.cells[i].cross(self.direction)
        for i in xrange(right_sol[-1] + runs[-1], len(self.cells)):
            self.cells[i].cross(self.direction)

    def solve_left(self, runs, run_index=0, span_start=0, in_span_start=0, seek_filled=False):
        if span_start >= len(self.spans):
            if run_index >= len(runs):
                return []
            else:
                raise InconsistencyException()
        span = self.spans[span_start]

        if run_index >= len(runs):
            for i in xrange(in_span_start, len(span)):
                if span[i]:
                    raise InconsistencyException()
            return self.solve_left(runs, run_index, span_start + 1)

        run = runs[run_index]

        if in_span_start >= len(span):
            return self.solve_left(runs, run_index, span_start + 1)

        if seek_filled:
            for i in xrange(in_span_start, min(len(span), in_span_start + run)):
                if span[i]:
                    seek_filled = False
                    break

        for i in xrange(in_span_start, len(span) - run + 1):
            if i > 0 and span[i-1]:
                raise InconsistencyException()
            if seek_filled and span[i + run - 1]:
                seek_filled = False
            if (not seek_filled) and (i + run == len(span) or not span[i+run]):
                try:
                    solution = self.solve_left(runs, run_index + 1, span_start, i + run + 1)
                    solution.insert(0, span.start_index + i)
                    return solution
                except InconsistencyException:
                    # If this fails, this run must include the next filled square!
                    seek_filled = True

        for i in xrange(max(in_span_start, len(span) - run), len(span)):
            if span[i]:
                raise InconsistencyException()

        return self.solve_left(runs, run_index, span_start + 1, seek_filled=seek_filled)

    def solve_right(self, runs, run_index=None, span_start=None, in_span_end=None, seek_filled=False):
        if span_start is None:
            span_start = len(self.spans) - 1
        if span_start < 0:
            if run_index < 0:
                return []
            else:
                raise InconsistencyException()
        span = self.spans[span_start]

        if in_span_end is None:
            in_span_end = len(span) - 1

        if run_index is None:
            run_index = len(runs) - 1
        if run_index < 0:
            for i in xrange(0, in_span_end + 1):
                if span[i]:
                    raise InconsistencyException()
            return self.solve_right(runs, run_index, span_start - 1)

        run = runs[run_index]

        if in_span_end < 0:
            return self.solve_right(runs, run_index, span_start - 1)
        in_span_start = in_span_end - run + 1

        if seek_filled:
            for i in xrange(max(0, in_span_start), in_span_start + run):
                if span[i]:
                    seek_filled = False
                    break

        for i in xrange(in_span_start, -1, -1):
            if i + run < len(span) and span[i+run]:
                raise InconsistencyException()
            if seek_filled and span[i]:
                seek_filled = False
            if (not seek_filled) and (i == 0 or not span[i-1]):
                try:
                    solution = self.solve_right(runs, run_index - 1, span_start, i - 2)
                    solution.append(span.start_index + i)
                    return solution
                except InconsistencyException:
                    seek_filled = True

        for i in xrange(0, min(in_span_end + 1, run)):
            if span[i]:
                raise InconsistencyException()

        return self.solve_right(runs, run_index, span_start - 1, seek_filled=seek_filled)


class CellSpan:
    def __init__(self, cells, start_index):
        self.cells = cells
        self.start_index = start_index
        # self.runs = None

    # def runs(self):
    #     if self.runs:
    #         return self.runs
    #     else:
    #         value = -1 # since we actually use None
    #         run = []
    #         for cell in self.cells:
    #             if cell.state != value and run:
    #                 yield value, run
    #                 value = cell.state
    #                 run = []
    #             run.append(cell)
    #         if run:
    #             yield value, run

    def __len__(self):
        return len(self.cells)

    def __getitem__(self, i):
        return self.cells[i]

    @staticmethod
    def split(cells):
        spans = []
        i = 0
        j = 0
        for j, cell in enumerate(cells):
            if cell.state == False:
                if i < j:
                    spans.append(CellSpan(cells[i:j], i))
                i = j + 1
        if i < len(cells):
            spans.append(CellSpan(cells[i:], i))
        return spans
