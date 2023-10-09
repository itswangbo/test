import random
import math
import sys
import os
import csv
from queue import Queue

LABEL = 0 # NOTE: to label each point
N_INSTANCE = 0
N_POINTS = 0
ACTIVE_POINTS = {} # NOTE: label to point
POINTS_IN_DAYS = Queue() # NOTE: a queue of list

class Fully_Cluster():
    def __init__(self, k, t, z, eps, radius):
        self.k = k
        self.t = t
        self.z = z
        self.eps = eps
        self.radius = radius

        self.n_cluster = 0
        ## NOTE: centers and corresponding clusters are initialized to 0
        self.centers = [0]*t
        self.clusters = [set() for _ in range(t+1)]

        self.selected_centers = []
        self.selected_clusters = []
        self.is_success = False
        self.true_radius = 0

    def fully_distance(self, f_point_index, s_point_index):
        f_point = ACTIVE_POINTS[f_point_index]
        s_point = ACTIVE_POINTS[s_point_index]
        return math.sqrt(sum([(float(a)-float(b))**2 for (a, b) in list(zip(f_point, s_point))]))

    def insert_last_center(self, point_index):
        self.clusters[self.n_cluster].add(point_index)

        if self.n_cluster < self.t:
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

    def new_fully_k_center_add(self, point_index, cluster_index, tot_points):
        if cluster_index == self.n_cluster:
            if self.n_cluster < self.t:
                self.insert_last_center(point_index)
            else:
                self.clusters[self.n_cluster].add(point_index)
        else:
            rd = random.randint(1, tot_points)
            if 1 == rd:
                deleted_points = self.delete_current_center(cluster_index)
                self.insert_last_center(point_index)

                for p_index in deleted_points:
                    self.fully_k_center_add(p_index)
            else:
                dist = self.fully_distance(point_index, self.centers[cluster_index])
                if self.radius*2 >= dist:
                    self.clusters[cluster_index].add(point_index)
                else:
                    tot_points = tot_points - len(self.clusters[cluster_index])
                    self.new_fully_k_center_add(point_index, cluster_index+1, tot_points)

    def new_fully_k_center_delete(self, point_index):
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

    def fully_k_center_greedy(self):
        s_relation = {}
        for i in range(self.n_cluster):
            s_relation[i] = set()
        for i in range(self.n_cluster):
            for j in range(i+1, self.n_cluster):
                dist = self.fully_distance(self.centers[i], self.centers[j])
                if self.radius*6 >= dist:
                    s_relation[i].add(j)
                    s_relation[j].add(i)

        self.selected_centers = []
        self.selected_clusters = []

        B_X = [0]*self.n_cluster
        for i in range(self.n_cluster):
            B_X[i] = len(self.clusters[i])
        W = set(range(self.n_cluster))
        n_covered_points = 0

        while len(self.selected_centers)<self.k and len(W)>0:
            B_hat_X = [0]*self.n_cluster
            for i in range(self.n_cluster):
                B_hat_X[i] = B_X[i] # + B_hat_X[i]
                for j in s_relation[i]:
                    B_hat_X[i] = B_hat_X[i]+B_X[j]
            selected_center_index, _ = max(enumerate(B_hat_X), key=lambda x: x[1]) # B_hat_X.index(max(B_hat_X))
            self.selected_centers.append(self.centers[selected_center_index])
            selected_cluster = []
            for center_index in W:
                dist = self.fully_distance(self.centers[center_index], self.centers[selected_center_index])
                if self.radius*12 >= dist:
                    selected_cluster.append(center_index)
                    n_covered_points = n_covered_points + B_X[center_index]
                    B_X[center_index] = 0
            self.selected_clusters.append(selected_cluster)
            for center in selected_cluster:
                W.remove(center)

        self.is_success = True if len(ACTIVE_POINTS)-n_covered_points > (1+self.eps)*self.z else False

    def fully_true_radius(self):
        dists = []
        for p_index in ACTIVE_POINTS:
            dist = sys.float_info.max ## NOTE: this is the maximal float
            for center_index in self.selected_centers:
                d = self.fully_distance(p_index, center_index)
                dist = min(dist, d)
            dists.append(dist)
        dists.sort()
        self.true_radius = dists[-math.floor((1+self.eps)*self.z+1)] # NOTE: need to plus 1

    def fully_get_centers(self):
        return [ACTIVE_POINTS[center_index] for center_index in self.selected_centers]

## BELOW IS THE MAIN PART

def read_next_day_points(levels, file_path: str):
    global LABEL, ACTIVE_POINTS, POINTS_IN_DAYS, N_POINTS

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) # skip the header

        points_in_the_day = []
        for row in csv_reader:
            cur_point = row[1:-1]
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
            level.fully_true_radius() ## NOTE: compute the true radius, just for testing, we can remove this line later
            if level.is_success is True:
                print(level.true_radius)
                return level.fully_get_centers()
        print("ERROR!")
        return None


if __name__ == "__main__":
    result_centers = get_centers(data_dir ="./data", s=1, k=2, t=100, z=9, tau=0.1, eps=0.1, d_min=0.1, d_max=10)
    print(result_centers)
          