import networkx as nx
import numpy as np

import sys
sys.path.append('..')

from student_utils import adjacency_matrix_to_graph, cost_of_solution
from phase2.solver_utils import parse_input, assign_dropoffs
import collections
import time

def greedy_shortest_path_solve(list_of_locations,
                               list_of_homes,
                               starting_car_location,
                               adjacency_matrix,
                               verbose=False,
                               params=[]):
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    source_idx = list_of_locations.index(starting_car_location)
    num_locs = len(G)
    
    home_idxs = set([list_of_locations.index(h) for h in list_of_homes])
    paths, all_pairs_dists = nx.floyd_warshall_predecessor_and_distance(G, weight='weight')
        
    def reconstruct_path(source, target, predecessors):
        if source == target:
            return []
        prev = predecessors[source]
        curr = prev[target]
        path = [target, curr]
        while curr != source:
            curr = prev[curr]
            path.append(curr)
        return list(reversed(path))
        
    traversal = [source_idx]
    
    # Find distances to previous node traversed
    dists = [
        (all_pairs_dists[traversal[-1]][h], h) for h in home_idxs
    ]
    
    while dists:
        n = min(dists, key=lambda x: x[0])
        dists.remove(n)
        n = n[1]
        traversal.extend(reconstruct_path(traversal[-1], n, paths)[1:])
        dists = [(all_pairs_dists[traversal[-1]][r], r) for _, r in dists]
        
    traversal.extend(reconstruct_path(traversal[-1], source_idx, paths)[1:])
 
    return traversal, assign_dropoffs(G, traversal, home_idxs, all_pairs_dists)
