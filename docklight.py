#!/usr/bin/env python

from math import sqrt
import os.path
import re
from sys import argv, exit, stderr

START_SYMBOL = '#SR,OK'

# unit conversion constants
SECONDS_PER_MINUTE = 60
SECONDS_PER_TEN_MINUTES = SECONDS_PER_MINUTE * 10
MILLISECONDS_PER_SECOND = 1000
MILLISECONDS_PER_TEN_MINUTES = MILLISECONDS_PER_SECOND * SECONDS_PER_TEN_MINUTES

# constants representing number of recordings made per unit time
TIMESTEPS_PER_SECOND = 5.0
TIMESTEPS_PER_MINUTE = TIMESTEPS_PER_SECOND * SECONDS_PER_MINUTE
TIMESTEPS_PER_MS = TIMESTEPS_PER_SECOND / MILLISECONDS_PER_SECOND
TIMESTEPS_PER_TEN_MINUTES = TIMESTEPS_PER_MS * MILLISECONDS_PER_TEN_MINUTES

# threshold for impossible distance movements
THRESHOLD = 25

# regular expression to capture start date and time
DATETIME_REGEX = re.compile(r'(\d?\d/\d?\d/\d\d\d\d) (\d?\d:\d\d:\d\d\.\d\d)')

def dist(x1, y1, x2, y2):
    """Computes the Euclidean distance between the two specified points."""
    return sqrt((x2-x1)**2 + (y2-y1)**2)

def avg(iterable):
    """Computes the arithmetic mean of the values in the specified iterable."""
    return sum(iterable) / float(len(iterable))

class Statistics:
    def __init__(self, input_file):
        # open the file, read the data, close the file
        f = open(input_file, 'r')
        self.data = f.readlines()
        f.close()

        # get the start and stop time from the first and last lines of the file
        lastline = self.data.pop()
        firstline = self.data.pop(0) 
        self.start_date, self.start_time = DATETIME_REGEX.search(firstline).group(1, 2)
        self.stop_date, self.stop_time = DATETIME_REGEX.search(lastline).group(1, 2)

        # find where the relevant data starts
        i = 0
        for line in self.data:
            i += 1
            if line.startswith(START_SYMBOL):
                break

        # get only relevant data and strip extra whitespace
        self.data = [line.strip() for line in self.data[i:]]

        # filter out any empty lines
        # TODO is this necessary?
        self.data = filter(lambda x: len(x) > 0, self.data)

        # strip '!OC,' and '<CR><LF>' and split on comma
        self.data = [coords[4:-8].split(',') for coords in self.data]

        self.positions = [(int(pos[0]), int(pos[1])) for pos in self.data]
        self.num_timesteps = len(self.positions)

        # compute distances from positions
        self.distances = []
        for i in range(1, self.num_timesteps):
            pre = self.positions[i-1]
            post = self.positions[i]
            self.distances.append(dist(pre[0], pre[1], post[0], post[1]))

        # distance measured in points per timestep
        self.total_distance = sum(self.distances)
        self.max_distance_per_timestep = max(self.distances)
        self.avg_distance_per_timestep = avg(self.distances)

        # distance with impossible distances filtered out
        self.trimmed_distances = filter(lambda x: x < THRESHOLD, self.distances)
        self.total_trimmed_distance = sum(self.trimmed_distances)
        self.max_trimmed_distance_per_timestep = max(self.trimmed_distances)
        self.avg_trimmed_distance_per_timestep = avg(self.trimmed_distances)

        # total distance travelled, adjusted to be for ten minutes
        self.adjusted_total_distance = self.avg_trimmed_distance_per_timestep * TIMESTEPS_PER_TEN_MINUTES

        # velocities measured in points per millisecond
        self.velocities = [d * TIMESTEPS_PER_MS for d in self.trimmed_distances]
        self.avg_velocity = self.avg_trimmed_distance_per_timestep * TIMESTEPS_PER_MS
        self.max_velocity = max(self.velocities)

    def __str__(self):
        """Returns a string representation of the statistics contained in this
        object. """
        return """Log file start date and time: {0}, {1}
Log file stop date and time: {2}, {3}

Number of recordings made: {4}
Total time of recordings, in milliseconds: {5}
Total time of recordings, in seconds: {6}
Total time of recordings, in minutes: {7}

Maximum distance traveled per timestep: {8}
Average distance traveled per timestep: {9}
Total distance traveled: {10}

Maximum "trimmed" distance traveled per timestep: {11}
Average "trimmed" distance traveled per timestep: {12}
Total trimmed distance traveled: {13}

Total distance traveled adjusted for ten minutes: {14}

Average velocity, in points per millisecond: {15}
Maximum velocity, in points per millisecond: {16}""".format(
            self.start_date, self.start_time,
            self.stop_date, self.stop_time,

            self.num_timesteps,
            self.num_timesteps / TIMESTEPS_PER_MS,
            self.num_timesteps / TIMESTEPS_PER_SECOND,
            self.num_timesteps / TIMESTEPS_PER_MINUTE,
            
            self.max_distance_per_timestep,
            self.avg_distance_per_timestep,
            self.total_distance,
            
            self.max_trimmed_distance_per_timestep,
            self.avg_trimmed_distance_per_timestep,
            self.total_trimmed_distance,
            
            self.adjusted_total_distance,
            self.avg_velocity,
            self.max_velocity
            )

if __name__ == '__main__':
    for argument in argv[1:]:
        if os.path.isfile(argument):
            statistics = Statistics(argument)
            print
            print statistics
            print
        else:
            stderr.write('warning: {0} is not a file; we ignored it\n'.format(argument))
