import csv
from queue import Queue
import math

from algo_fully_adv import Fully_adv_cluster

LABEL = 0 # NOTE: to label each point
N_INSTANCE = 0
N_POINTS = 0
ACTIVE_POINTS = {} # NOTE: label to point
POINTS_IN_DAYS = Queue() # NOTE: a queue of list

def read_next_day_points(file_path: str):
    global LABEL, ACTIVE_POINTS, POINTS_IN_DAYS, N_POINTS

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # skip the header

        points_in_the_day = []
        for row in csv_reader:
            cur_point = row[:-1]
            ACTIVE_POINTS[LABEL] = cur_point
            points_in_the_day.append(LABEL)
            LABEL = LABEL+1
            N_POINTS = N_POINTS+1
        POINTS_IN_DAYS.put(points_in_the_day)

def delete_previous_day_points():
    global POINTS_IN_DAYS, ACTIVE_POINTS, N_POINTS

    points_in_the_day = POINTS_IN_DAYS.get()
    for point in points_in_the_day:
        ACTIVE_POINTS.pop(point)
        N_POINTS = N_POINTS-1

def fully_initialize_level_array(k, t, tau, d_min, d_max):
    global N_INSTANCE
    N_INSTANCE = 1+math.ceil(math.log(d_max/d_min)/math.log(1.0 + tau))
    radius = d_min

    levels = []
    for _ in range(N_INSTANCE):
        level = Fully_adv_cluster(k, t, radius)
        levels.append(level)
        radius = radius*(1.0+tau)
    return levels

# def main():
#     levels = fully_initialize_level_array()
#     read_next_day_points()
#     delete_previous_day_points()