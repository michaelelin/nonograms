import argparse
import time

from nonograms.data import GridData, RandomGridData, NONOGRAMS_PATH
from nonograms.view import GuiView
from nonograms.solve import NonogramProblem
from benchmark import NonogramsBenchmark

def view(args):
    data = GridData.load(args.file)
    grid = data.get(args.id)
    GuiView(grid)

def solve(args):
    if args.random:
        data = RandomGridData(args.random)
    else:
        data = GridData.load(args.file)
    grid = data.get(args.id)
    grid.clear()
    problem = NonogramProblem(grid)
    if args.graphics:
        GuiView(grid, scale=args.size)
    else:
        start_time = time.clock()
        problem.solve()
        print('Solved in %s seconds with %s branching attempts' % (time.clock() - start_time,
                                                                   problem.branching_attempts))

def benchmark(args):
    benchmark = NonogramsBenchmark(GridData.load(args.file))
    benchmark.test(timeout=args.timeout)
    benchmark.report()
    if args.out:
        benchmark.save(args.out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve a nonogram.')
    subparsers = parser.add_subparsers()


    # nonograms.py view ...
    parse_view = subparsers.add_parser('view',
                                       help='view a puzzle by ID')
    parse_view.add_argument('id',
                            type=int,
                            help='the puzzle ID')
    parse_view.add_argument('-f', '--file',
                            default=NONOGRAMS_PATH,
                            help='the puzzle data file to use (default: %s)' % NONOGRAMS_PATH)
    parse_view.set_defaults(func=view)


    # nonograms.py solve ...
    parse_solve = subparsers.add_parser('solve',
                                        help='solve a puzzle by ID')
    parse_solve.add_argument('id',
                             type=int,
                             help='the puzzle ID')
    parse_solve.add_argument('-f', '--file',
                             default='data/nonograms.json',
                             help='the puzzle data file to use (default: %s)' % NONOGRAMS_PATH)
    parse_solve.add_argument('-r', '--random',
                             type=int,
                             default=None,
                             help='If used, generates a random puzzle instead of the given size')
    parse_solve.add_argument('-g', '--graphics',
                             action='store_true',
                             help='show a GUI while solving')
    parse_solve.set_defaults(func=solve)

    parse_solve.add_argument('-s', '--size',
                             type=int,
                             default=12)

    # nonograms.py benchmark ...
    parse_benchmark = subparsers.add_parser('benchmark',
                                            help='time solving a set of puzzles')
    parse_benchmark.add_argument('-f', '--file',
                                 default='data/nonograms.json',
                                 help='the puzzle data file to use (default: %s)' % NONOGRAMS_PATH)
    parse_benchmark.add_argument('-t', '--timeout',
                                 default=None,
                                 type=float,
                                 help='timeout per puzzle (in seconds) (default: none)')
    parse_benchmark.add_argument('-o', '--out',
                                 default=None,
                                 help='the file to output results to')
    parse_benchmark.set_defaults(func=benchmark)


    args = parser.parse_args()
    args.func(args)
