import random
import math
import sys
import os
import csv
from queue import Queue
from datetime import datetime
import numpy as np

LABEL = 0 # NOTE: to label each point
N_INSTANCE = 0
N_POINTS = 0
ACTIVE_POINTS = {} # NOTE: label to point
POINTS_IN_DAYS = Queue() # NOTE: a queue of list

class Fully_Cluster():
    def __init__(self, k, eps, radius):
        self.k = k
        self.eps = eps
        self.radius = radius

        self.n_cluster = 0
        ## NOTE: centers and corresponding clusters are initialized to 0
        self.centers = [0]*k
        self.clusters = [set() for _ in range(k+1)]

        self.true_radius = 0
        
    def fully_distance(self, f_point_index, s_point_index):
        f_point = ACTIVE_POINTS[f_point_index]
        s_point = ACTIVE_POINTS[s_point_index]
        return np.sqrt(np.sum((np.array(f_point).astype(np.float64) - np.array(s_point).astype(np.float64)) ** 2))

    def insert_last_center(self, point_index):
        self.clusters[self.n_cluster].add(point_index)

        if self.n_cluster < self.k:
            self.centers[self.n_cluster] = point_index
            self.n_cluster = self.n_cluster+1

    def fully_k_center_add(self, point_index):
        for c_index in range(self.n_cluster):
            dist = self.fully_distance(point_index, self.centers[c_index])
            if self.radius*2 >= dist:
                self.clusters[c_index].add(point_index)
                return
        self.insert_last_center(point_index)

    def delete_current_center(self, cluster_index):
        deleted_points = []
        for c_index in range(cluster_index, self.n_cluster+1):
            deleted_points.extend(list(self.clusters[c_index]))
            self.clusters[c_index].clear()

        self.n_cluster = cluster_index
        
        random.shuffle(deleted_points)
        return deleted_points

    def fully_k_center_delete(self, point_index):
        c_index = 0
        for c_index in range(self.n_cluster):
            if point_index in self.clusters[c_index]:
                self.clusters[c_index].remove(point_index)
                if point_index == self.centers[c_index]:
                    deleted_points = self.delete_current_center(c_index)
                    for p_index in deleted_points:
                        self.fully_k_center_add(p_index)
                return
        self.clusters[c_index].remove(point_index)

    def fully_true_radius(self):
        true_radius = sys.float_info.min
        for p_index in ACTIVE_POINTS:
            dist = sys.float_info.max ## NOTE: this is the maximal float
            for center_index in self.centers:
                d = self.fully_distance(p_index, center_index)
                dist = min(dist, d)
            true_radius = max(true_radius, dist)
        self.true_radius = true_radius

    def fully_get_centers(self):
        return [ACTIVE_POINTS[center_index] for center_index in self.centers]
    
    def fully_get_cardinality(self):
        cars = []
        sz = len(self.clusters)-1
        for i in range(sz):
            cars.append(len(self.clusters[i]))
        return cars


## BELOW IS THE MAIN PART

def read_next_day_points(levels, file_path: str):
    global LABEL, ACTIVE_POINTS, POINTS_IN_DAYS, N_POINTS

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # skip the header

        points_in_the_day = []
        for row in csv_reader:
            if int(row[0])%50 == 0:
                print("current row: ", row[0])
                print("current time: ", datetime.now().strftime("%H:%M:%S"))
            # cur_point = row[1:-1]
            cur_point = row[1:-1]
            ACTIVE_POINTS[LABEL] = cur_point
            N_POINTS = N_POINTS+1
            points_in_the_day.append(LABEL)
            for level in levels:
                level.fully_k_center_add(LABEL)
            LABEL = LABEL+1
        POINTS_IN_DAYS.put(points_in_the_day)

def delete_previous_day_points(levels):
    global POINTS_IN_DAYS, ACTIVE_POINTS, N_POINTS

    points_in_the_day = POINTS_IN_DAYS.get()
    for point in points_in_the_day:
        ACTIVE_POINTS.pop(point)
        N_POINTS = N_POINTS-1
        for level in levels:
            level.fully_k_center_delete(point)

def fully_initialize_level_array(k, eps, d_min, d_max):
    global N_INSTANCE
    N_INSTANCE = 1+math.ceil(math.log(d_max/d_min)/math.log(1.0 + eps))
    radius = d_min

    levels = []
    for _ in range(N_INSTANCE):
        level = Fully_Cluster(k, eps, radius)
        levels.append(level)
        radius = radius*(1.0+eps)
    return levels

def get_centers(data_dir, s, k, eps, d_min, d_max):
    levels = fully_initialize_level_array(k, eps, d_min, d_max)

    print(f"LEN of LEVELS[{len(levels)}]")

    file_names = os.listdir(data_dir)
    file_names = sorted(file_names)

    for file_name in file_names:
        file_path = os.path.join(data_dir, file_name)
        read_next_day_points(levels, file_path)
        if POINTS_IN_DAYS.qsize() > s:
            delete_previous_day_points(levels)
        for level in levels:
            print(f"UNCLUSTERED POINTS[{len(level.clusters[k])}]")
            if len(level.clusters[k])==0:
                level.fully_true_radius() ## NOTE: compute the true radius, just for testing, we can remove this line later
                print(level.radius)
                print(level.true_radius)
                cars = level.fully_get_cardinality()
                print(cars)
                return level.fully_get_centers()
        print("ERROR!")
        return None

def main():
    result_centers = get_centers(data_dir ="./data", s=1, k=2, eps=0.01, d_min=200, d_max=280)
    print(len(result_centers))

if __name__ == '__main__':
    main()

# import cProfile
# if __name__ == '__main__':
#     cProfile.run('main()')



# min_dist = sys.float_info.max
# max_dist = 0
# file_path = "./data/tweets_bert_2018_0.csv" ## NOTE: to be edited

# with open(file_path, 'r') as csv_file:
#     csv_reader = csv.reader(csv_file)
#     next(csv_reader) # skip the header

#     points_in_the_day = []
#     for row in csv_reader:
#         cur_point = row[1:-1]
#         points_in_the_day.append(cur_point)
#     lens = len(points_in_the_day)
#     for i in range(lens):
#         for j in range(i+1, lens):
#             dist = math.sqrt(sum([(float(a)-float(b))**2 for (a, b) in list(zip(points_in_the_day[i], points_in_the_day[j]))]))
#             min_dist = min(min_dist, dist)
#             max_dist = max(max_dist, dist)
#     print(min_dist, max_dist)
