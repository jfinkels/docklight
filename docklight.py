#!/usr/bin/env python

from sys import argv, exit
from math import sqrt

START_SYMBOL = '#SR,OK'

SECONDS_PER_MINUTE = 60
SECONDS_PER_TEN_MINUTES = SECONDS_PER_MINUTE * 10
MILLISECONDS_PER_SECOND = 1000
MILLISECONDS_PER_TEN_MINUTES = MILLISECONDS_PER_SECOND * SECONDS_PER_TEN_MINUTES

RECORDINGS_PER_SECOND = 5
RECORDINGS_PER_MS = RECORDINGS_PER_SECOND / float(MILLISECONDS_PER_SECOND)
RECORDINGS_PER_TEN_MINUTES = RECORDINGS_PER_MS * MILLISECONDS_PER_TEN_MINUTES

# threshold for impossible distance movements
THRESHOLD = 25

def distance(x1, y1, x2, y2):
    """Computes the distance between the two specified points."""
    return sqrt((x2-x1)**2 + (y2-y1)**2)

def avg(iterable):
    """Computes the arithmetic mean of the values in the specified iterable."""
    return sum(iterable) / float(len(iterable))

if len(argv) < 2:
    print 'Must provide an input file as an argument.'
    exit(-1)
    
# get the data from the input file
input_file = open(argv[1], 'r')
all_data = input_file.readlines()
input_file.close()

# find where the data starts
i = 0
for line in all_data:
    i += 1
    if line.startswith(START_SYMBOL):
        break

# strip extra whitespace
all_data = [line.strip() for line in all_data[i:]]

# filter out any empty lines
all_data = filter(lambda x: len(x) > 0, all_data)

# strip '!OC,' and '<CR><LF>' and split on comma
all_data = [coords[4:-8].split(',') for coords in all_data]

# strip terminal log file notice
all_data = all_data[:-1]

# turn the strings into numbers
all_data = [(int(coords[0]), int(coords[1])) for coords in all_data]

# compute the distances
distances = []
for i in range(1, len(all_data)):
    before = all_data[i-1]
    after = all_data[i]
    distances.append(distance(before[0], before[1], after[0], after[1]))

# filter out distances which are impossible
trimmed_distances = filter(lambda x: x < THRESHOLD, distances)

# compute the velocities, in points per millisecond
velocities = [d * RECORDINGS_PER_MS for d in trimmed_distances]

# number of recordings
num_recordings = len(all_data)

# total distance
total_distance = sum(distances)

# max distance per timestep
max_distance_per_timestep = max(distances)

# average distance per timestep
avg_distance_per_timestep = avg(distances)

# "trimmed" total distance
total_trimmed_distance = sum(trimmed_distances)

# "trimmed" max distance per timestep
max_trimmed_distance_per_timestep = max(trimmed_distances)

# "trimmed" average distance per timestep
avg_trimmed_distance_per_timestep = avg(trimmed_distances)

# "trimmed" total distance adjusted to ten minutes
adjusted_total_distance = avg_trimmed_distance_per_timestep * RECORDINGS_PER_TEN_MINUTES

# adjusted velocity = average trimmed distance per millisecond
avg_velocity = avg_trimmed_distance_per_timestep * RECORDINGS_PER_MS

# max velocity per timestep
max_velocity = max(velocities)

print 'Number of recordings made:', num_recordings
print 'Total time of recordings, in milliseconds:', num_recordings / RECORDINGS_PER_MS
print
print 'Maximum distance traveled per timestep:', max_distance_per_timestep
print 'Average distance traveled per timestep:', avg_distance_per_timestep
print 'Total distance traveled:', total_distance
print
print 'Maximum "trimmed" distance traveled per timestep:', max_trimmed_distance_per_timestep
print 'Average "trimmed" distance traveled per timestep:', avg_trimmed_distance_per_timestep
print 'Total trimmed distance traveled:', total_trimmed_distance
print
print 'Total distance traveled adjusted for ten minutes:', adjusted_total_distance
print
print 'Average velocity, in points per millisecond:', avg_velocity
print 'Maximum velocity, in points per millisecond:', max_velocity
