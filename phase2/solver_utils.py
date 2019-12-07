def parse_input(filepath):
    """
    Parses an input file into its respective parts.
    Returns:
        num_locations:  (int) total number of locations
        num_houses:     (int) number of houses
        location_names: List[str] of names of each location
        house_names:    List[str] of names for each TA house 
        source:         (str) name of the source vertex
        adj:            (List[List[float or 'x']]) adjacency matrix of the graph, with
                        'x' representing no edge, and a float value for the weight of
                        an edge that exists in the graph
    """

    with open(filepath, 'r') as f:
        num_locations = int(f.readline())
        num_houses = int(f.readline())
        location_names = f.readline().rstrip()
        location_names = location_names.split(' ')
        house_names = f.readline().rstrip()
        house_names = house_names.split(' ')
        source = f.readline().rstrip()
        
        def process_row(row):
            for i in range(len(row)):
                if row[i] != 'x':
                    row[i] = float(row[i])
            return row
        
        try:
            adj = [
                process_row(f.readline().rstrip().split(' '))
                for i in range(num_locations)
            ]
        except:
            adj = [
                process_row(f.readline().rstrip().split('\t'))
                for i in range(num_locations)
            ]
        
    return num_locations, num_houses, location_names, house_names, source, adj

def path_to_edges(path):
    edges = []
    for i in range(len(path) - 1):
        edges.append((path[i], path[i + 1]))
    return edges

def assign_dropoffs(G, path, homes_idxs, all_pairs_dists):
    """
    Returns the dictionary of all dropoffs along this path.
    """
    locations_on_path = set(path)
    dropoffs = collections.defaultdict(list)
    for h in homes_idxs:
        closest_loc_on_path = min(locations_on_path,
                                  key=lambda loc: all_pairs_dists[h][loc])
        dropoffs[closest_loc_on_path].append(h)
    return dropoffs

