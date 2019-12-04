import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

import sys
sys.path.append('..')
from student_utils import adjacency_matrix_to_graph
import collections

from student_utils import cost_of_solution
from itertools import islice
import time

def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))

def local_search_solve(list_of_locations,
                       list_of_homes,
                       starting_car_location,
                       adjacency_matrix,
                       initial_solution=None,
                       params=[]):

    start = time.time()
    # Generate initial solution (random or greedy algorithm)
    if not initial_solution:
        current_solution = mst_dfs_solve(list_of_locations,
                                         list_of_homes,
                                         starting_car_location,
                                         adjacency_matrix,
                                         params=params)
    else:
        current_solution = initial_solution

    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    
    home_idxs = [list_of_locations.index(h) for h in list_of_homes]
    all_pairs_dists = nx.floyd_warshall(G, weight='weight')
    
    def get_neighbors(G, path):
        """
        Returns "1-change" neighbors, which are all paths that:
            Either include a vertex that is not visited in path
            Include a vertex visited in path
            Swap a vertex that is visited with a vertex not visited
        """
        visited = set(path)
        unvisited = set(range(len(G))) - visited

        occurences = collections.Counter(path)

        neighbors = []

        # Exclude a vertex
        for vertex_to_exclude in visited - {0}:
            new_path = path.copy()
    #         print(f'VERTEX TO EXCLUDE: {vertex_to_exclude}')

            for i in range(occurences[vertex_to_exclude]):
                idx = new_path.index(vertex_to_exclude)
                prev, nxt = new_path[idx - 1], new_path[idx + 1]
                if prev == nxt:  # Able to skip over visiting
                    new_path.pop(idx)
                    new_path.pop(idx)
                else:
                    two_shortest = k_shortest_paths(G, source=prev, target=nxt,
                                                    k=2, weight='weight')
                    for alt_path in two_shortest:
                        if alt_path != path[idx-1:idx+2] and vertex_to_exclude not in alt_path:
                            new_path.pop(idx)
                            new_path = new_path[:idx-1] + alt_path + new_path[idx+1:]
                            break
                if vertex_to_exclude not in new_path:
#                     print(f'REMOVING {vertex_to_exclude}: {new_path}')
                    neighbors.append(new_path)
        
        # Include a vertex
        for vertex_to_include in unvisited:
            new_path = path.copy()

            one_away = []
            for v in visited:
                if vertex_to_include in G.neighbors(v):
                    one_away.append(v)
            if not one_away:
                continue
    #         print(f'\nVERTEX TO INCLUDE: {vertex_to_include}')
            closest_neighbor = min(one_away, key=lambda n: G[vertex_to_include][n]['weight'])
            # Get the index of the closest neighbor, check if a path exists between 
            # the vertex being added and the next vertex in the path. If so, a better
            # detour exists than the trivial path to the new vertex and directly back.
            closest_idx = new_path.index(closest_neighbor)
            if G.has_edge(vertex_to_include, new_path[closest_idx + 1]):
                new_path.insert(closest_idx + 1, vertex_to_include)
            else:
                new_path.insert(closest_idx + 1, closest_neighbor)
                new_path.insert(closest_idx + 1, vertex_to_include)
#             print(f'ADDING {vertex_to_include}: {new_path}')
            neighbors.append(new_path)

        # Swap a vertex (maybe add this)

        return neighbors

    def assign_dropoffs(G, path, home_idxs):
        """
        Returns the dictionary of all dropoffs along this path.
        """
        locations_on_path = set(path)
        dropoffs = collections.defaultdict(list)
    #     print(locations_on_path)
        for h in home_idxs:
    #         print(f'DISTANCES FOR {h}', all_pairs_dists[h])
            closest_loc_on_path = min(locations_on_path, key=lambda loc: all_pairs_dists[h][loc])
            dropoffs[closest_loc_on_path].append(h)
        return dropoffs

    def evaluate(G, path, home_idxs, verbose=False):
        """
        Assigns optimal dropoff locations for each TA, given a path that the car
        is going to take, and calculate the total energy expended. This is the
        metric that neighbors are going to be evaluated on.
        """
        dropoffs = assign_dropoffs(G, path, home_idxs)
        cost, msg = cost_of_solution(G, path, dropoffs, shortest=all_pairs_dists)
        if verbose:
            print(msg)

        return cost
    
#     print(get_neighbors(G, current_solution))
#     print(assign_dropoffs(G, current_solution, home_idxs))
    
    i = 0
    current_cost = evaluate(G, current_solution, home_idxs)
    
#     epsilon = 0.1
    epsilon = 0
    epsilon_decay_factor = 0.95
    while True:  # TODO(justinvyu): Add a timeout
        start_iter = time.time()
        neighbors = get_neighbors(G, current_solution.copy())
        
        # Take a random action with epsilon probability, decaying over time
        if np.random.rand() < epsilon:
            current_solution = neighbors[np.random.randint(len(neighbors))]
            current_cost = evaluate(G, current_solution, home_idxs)
            print(f'=== Iteration #{i}, Epsilon = {epsilon} ==='
                  f'\n Picked a RANDOM neighbor, Cost = {current_cost}')
            epsilon *= epsilon_decay_factor
            
        # print(f'\nSearching over {len(neighbors)} neighbors...')
        best_neighbor = min(neighbors, key=(
            lambda neighbor_sol: evaluate(G, neighbor_sol, home_idxs)))
        best_cost = evaluate(G, best_neighbor, home_idxs, verbose=False)
        if best_cost < current_cost:
            # print(f'=== Iteration #{i}, Epsilon = {epsilon} === \n Improved Cost = {best_cost}')
            current_solution = best_neighbor
            current_cost = best_cost
        else:
            print(f'Local search took: {time.time() - start} seconds')
            print(f'Local search terminated with solution (cost={current_cost}): {current_solution}')
            evaluate(G, current_solution, home_idxs, verbose=True)
            return current_solution, assign_dropoffs(G, current_solution, home_idxs)
        i += 1
        epsilon *= epsilon_decay_factor
        end_iter = time.time()
        # print(f'Iteration took {end_iter - start_iter} s')

if __name__ == '__main__':
    # input_path = '../phase1/100.in'
    input_path = '../phase2/test_inputs/branching_20v_5h.in'
    (num_locations,
     num_houses,
     location_names,
     house_names,
     source,
     adj) = parse_input(input_path)
    G, _ = adjacency_matrix_to_graph(adj)
    # path = dijkstra_greedy_solve(location_names, house_names, source, adj)
    path, best_cost = local_search_solve(location_names, house_names, source, adj)

    edges_to_draw = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edges_to_draw.append((u, v))
    print(edges_to_draw)
    plot_graph(input_path,
               layout_style=nx.kamada_kawai_layout,
               show_edge_weights=True,
               edges_to_draw=edges_to_draw,
               directed=True)
