import random
import math
from main import ACTIVE_POINTS

class Fully_adv_cluster():
    def __init__(self, k, t, radius):
        self.k = k
        self.t = t
        self.radius = radius

        self.n_cluster = 0
        self.centers = []
        self.clusters = []

        self.selected_centers = []
        self.covered_points = 0

    def fully_distance(self, f_point_index, s_point_index):
        f_point = ACTIVE_POINTS[f_point_index]
        s_point = ACTIVE_POINTS[s_point_index]
        return math.sqrt(sum([(a-b)**2 for (a, b) in zip(f_point, s_point)]))

    def fully_k_center_add(self, point_index):
        for c_index in range(self.n_cluster):
            dist = self.fully_distance(point_index, self.centers[c_index])
            if self.radius*2 >= dist:
                self.clusters[c_index].add(point_index)
                return

        self.clusters[self.n_cluster].add(point_index)

        if self.n_cluster < self.t:
            self.centers[self.n_cluster] = point_index
            
            self.n_cluster = self.n_cluster+1
            self.clusters[self.n_cluster] = set()

    def insert_last_center(self, point_index):
        if len(self.clusters) <= self.n_cluster:
            self.clusters[self.n_cluster] = set()
        self.clusters[self.n_cluster].add(point_index)

        self.centers[self.n_cluster] = point_index
        self.n_cluster = self.n_cluster+1

    def delete_current_center(self, cluster_index):
        deleted_points = []
        for c_index in range(cluster_index, self.n_cluster):
            deleted_points.extend(list(self.clusters[c_index]))
            self.clusters[c_index] = set()

        self.n_cluster = cluster_index
        
        random.shuffle(deleted_points)
        return deleted_points

    def new_fully_k_center_add(self, point_index, cluster_index, tot_points):
        if cluster_index == self.n_cluster:
            if self.n_cluster < self.t:
                self.insert_last_center(point_index)
            else:
                if len(self.clusters) <= self.n_cluster:
                    self.clusters[self.n_cluster] = set()
                self.clusters[self.n_cluster].add(point_index)
        else:
            rd = random.randint(1, tot_points)
            if 1 == rd % tot_points:
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
        while c_index < self.n_cluster:
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
            for j in range(i+1, self.n_cluster):
                dist = self.fully_distance(self.centers[i], self.centers[j])
                if self.radius*6 >= dist:
                    if i not in s_relation:
                        s_relation[i] = set()
                    if j not in s_relation:
                        s_relation[j] = set()
                    s_relation[i].add(j)
                    s_relation[j].add(i)

        selected_centers = []
        selected_clusters = []

        B_X = [0]*self.n_cluster
        for i in range(self.n_cluster):
            B_X[i] = len(self.clusters[i])
        W = set(range(self.n_cluster))

        while len(selected_centers)<=self.k and len(W)>0:
            B_hat_X = [0]*self.n_cluster
            for i in range(self.n_cluster):
                B_hat_X[i] = B_hat_X[i]+B_X[i]
                for j in s_relation[i]:
                    B_hat_X[i] = B_hat_X[i]+B_X[j]
            selected_center_index = B_hat_X.index(max(B_hat_X))
            selected_centers.append(self.centers[selected_center_index])
            selected_cluster = []
            for center_index in W:
                dist = self.fully_distance(self.centers[center_index], self.centers[selected_center_index])
                if self.radius*12 >= dist:
                    selected_cluster.append(center_index)
                    B_X[center_index] = 0
            selected_clusters.append(selected_cluster)
            for center in selected_cluster:
                W.remove(center)