import json
import time
from collections import defaultdict
from tqdm import tqdm

from nonograms.solve import NonogramProblem

class NonogramsBenchmark:
    def __init__(self, data):
        self.data = data

    def test(self, timeout=None):
        self.timeout = timeout
        print('Timing performance on %s puzzles...' % len(self.data))
        self.results = {}
        try:
            for grid in tqdm(self.data, smoothing=0):
                grid.clear()
                problem = NonogramProblem(grid)
                start_time = time.clock()
                try:
                    problem.solve(abort_time=(start_time + timeout if timeout else None))
                    solve_time = time.clock() - start_time
                    self.report_result(grid.nid, solve_time)
                except RuntimeError as e:
                    self.report_result(grid.nid, error=e)
        except KeyboardInterrupt:
            # We're done here anyway, so finish up and possibly report the results
            pass

    def report_result(self, nid, time=None, error=None):
        if error:
            self.results[nid] = { 'time': time, 'error': type(error).__name__ }
        else:
            self.results[nid] = { 'time': time }

    def report(self):
        completed_times = []
        errors = defaultdict(lambda: 0)
        for result in self.results.values():
            if 'error' in result:
                errors[result['error']] += 1
            else:
                completed_times.append(result['time'])
        completed_times.sort()

        print('Mean solve time:   %s' % (sum(completed_times) / len(completed_times)))
        print('Median solve time: %s' % completed_times[len(completed_times)/2])
        print('Max solve time:    %s' % max(completed_times))
        print('Completed: %s' % len(completed_times))
        print('Errors: %s' % sum(errors.values()))
        for error, count in errors.items():
            print('  %s: %s' % (error, count))

    def save(self, filename):
        print('Saving results to %s' % filename)
        with open(filename, 'w') as f:
            json.dump({
                'timeout': self.timeout,
                'results': self.results
            }, f)

