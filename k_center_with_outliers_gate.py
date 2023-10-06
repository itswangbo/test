import os
import csv
from queue import Queue
import math

from algo_fully_dyn import Fully_Cluster

LABEL = 0 # NOTE: to label each point
N_INSTANCE = 0
N_POINTS = 0
ACTIVE_POINTS = {} # NOTE: label to point
POINTS_IN_DAYS = Queue() # NOTE: a queue of list

def read_next_day_points(levels, file_path: str):
    global LABEL, ACTIVE_POINTS, POINTS_IN_DAYS, N_POINTS

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # skip the header

        points_in_the_day = []
        for row in csv_reader:
            cur_point = row[:-1]
            ACTIVE_POINTS[LABEL] = cur_point
            N_POINTS = N_POINTS+1
            points_in_the_day.append(LABEL)
            for level in levels:
                level.new_fully_k_center_add(LABEL, 0, N_POINTS)
            LABEL = LABEL+1
        POINTS_IN_DAYS.put(points_in_the_day)

def delete_previous_day_points(levels):
    global POINTS_IN_DAYS, ACTIVE_POINTS, N_POINTS

    points_in_the_day = POINTS_IN_DAYS.get()
    for point in points_in_the_day:
        ACTIVE_POINTS.pop(point)
        N_POINTS = N_POINTS-1
        for level in levels:
            level.new_fully_k_center_delete(point)

def fully_initialize_level_array(k, t, z, tau, eps, d_min, d_max):
    global N_INSTANCE
    N_INSTANCE = 1+math.ceil(math.log(d_max/d_min)/math.log(1.0 + tau))
    radius = d_min

    levels = []
    for _ in range(N_INSTANCE):
        level = Fully_Cluster(k, t, z, eps, radius)
        levels.append(level)
        radius = radius*(1.0+tau)
    return levels

def get_centers(data_dir, s, k, t, z, tau, eps, d_min, d_max):
    levels = fully_initialize_level_array(k, t, z, tau, eps, d_min, d_max)

    file_names = os.listdir(data_dir)
    file_names = sorted(file_names)

    for file_name in file_names:
        file_path = os.path.join(data_dir, file_name)
        read_next_day_points(levels, file_path)
        if POINTS_IN_DAYS.qsize() > s:
            delete_previous_day_points(levels)
        for level in levels:
            level.fully_k_center_greedy()
            level.fully_true_radius() ## NOTE: compute the true radius, just for testing, we can remove this line
            if level.is_success is True:
                print(level.true_radius)
                return level.selected_centers
        print("ERROR!")
        return None