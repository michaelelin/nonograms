import itertools
import json
import sys

INCREMENT = 0.01

def data_points(filename):
    with open(filename, 'r') as f:
        results = json.load(f)
    times = sorted(result['time'] for nid, result in results['results'].iteritems() if result['time'])
    count = 0
    points = []
    time_cap = 0.0
    for i, time in enumerate(times):
        while time > time_cap:
            points.append((i, time_cap))
            time_cap += INCREMENT
    points.append((len(times), time_cap))
    return points


if __name__ == '__main__':
    filename = sys.argv[1]
    print(','.join(['{%s,%s}' % point for point in data_points(filename)]))
