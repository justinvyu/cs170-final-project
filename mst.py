import networkx as nx
from student_utils import adjacency_matrix_to_graph, is_valid_walk, cost_of_solution, convert_locations_to_indices
def mst_dfs_solve(list_of_locations,
                  list_of_homes,
                  starting_car_location,
                  adjacency_matrix,
                  params=[]):
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    
    mst = nx.minimum_spanning_tree(G)
    seen = set()
    traversal = []
    def dfs(u):
        if u not in seen:
            traversal.append(u)
            seen.add(u)
            for v in mst.neighbors(u):
                if v not in seen:
                    dfs(v)
                    traversal.append(u)
    dfs(list_of_locations.index(starting_car_location))
    
    dropoffs = {
        home: [home] for home in list_of_homes 
    }
    dropoffs = {list_of_locations.index(key): convert_locations_to_indices(dropoffs[key], list_of_locations) for key in dropoffs}
    return traversal, dropoffs
