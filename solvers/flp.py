import networkx as nx
from student_utils import adjacency_matrix_to_graph, is_valid_walk, cost_of_solution, convert_locations_to_indices
from collections import defaultdict
def flp_solve(list_of_locations,
                  list_of_homes,
                  starting_car_location,
                  adjacency_matrix,
                  solve,
                  params=[]):
    mapping = defaultdict(int)
    for i in range(len(list_of_locations)):
        mapping[list_of_locations[i]] = i
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    U = list_of_homes
    facilities = list_of_locations
    start = starting_car_location
    paths, distances = nx.floyd_warshall_predecessor_and_distance(G, weight='weight')
#     print(distances)
#     print(paths)
# print("ran all pairs")
    # Builds set S in polynomial time as opposed to powerset (exponential)
    def buildS():
        res = []
        for f in facilities:
            for s in range(1, len(U)):
                sorted_dist = sorted([(target, distances[mapping[f]][mapping[target]]) for target in U], key=lambda x: x[1])
                sorted_dist = sorted_dist[:s]
                A = set([t for t, _ in sorted_dist])
                cost = sum([s[1] for s in sorted_dist]) + (2/3) * distances[mapping[start]][mapping[f]]
                elem = {'facility': f, 
                        'A': A, 
                        'count': s, 
                        'cost': cost
                       } # facility, dictionary to see which elements are present, num elements, cost
                res.append(elem)
        return res
    S = buildS()
   # print("Built S")
    uncovered = set(U)
    lst = [(s['cost']/s['count'], hash(s['facility'] + str(s['count'])), s) for s in S]
    result = set([])
    dropoff_mapping = defaultdict(list)
    while uncovered and lst:
        smallest = min(lst, key = lambda x: x[0])
        lst.remove(smallest)
        smallest = smallest[2]
        result.add(smallest['facility'])
        dropoff_mapping[smallest['facility']] = list(smallest['A'])
        uncovered = uncovered.difference(smallest['A'])
        new_lst = []
        for _, h, elem in lst:
            if solve == 1:
                if elem['facility'] in result:
                    elem['cost'] -= distances[mapping[start]][mapping[elem['facility']]]
            if solve == 2:
                if elem['facility'] not in result:
                    elem['cost'] = sum([distances[mapping[s]][mapping[elem['facility']]] for s in elem['A']]) + (1/4) * sum([distances[mapping[r]][mapping[elem['facility']]] for r in result if r != start])
            intersect = len(elem['A'].intersection(uncovered))
            new_cost = float('inf')
            if intersect > 0:
                new_cost = elem['cost']/intersect
            new_lst.append((new_cost, h, elem))
        lst = new_lst
   # print("computed dropoffs")
    #finding path between all
    traversal = [mapping[start]]
    dists = [(distances[traversal[-1]][mapping[r]], mapping[r]) for r in list(result) if r != start]
    dropoffs = [mapping[start]] if start in result else []
   # print("computing traversal")
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
        
    while dists:
        n = min(dists, key= lambda x: x[0])
        dists.remove(n)
        n = n[1]
        dropoffs.append(n)
        traversal.extend(reconstruct_path(traversal[-1], n, paths)[1:])
        dists = [(distances[traversal[-1]][r], r) for _, r in dists]
    traversal.extend(reconstruct_path(traversal[-1], mapping[start], paths)[1:]) 
   # print("done")
#     dropoffs_dict = {key: dropoff_mapping[key] for key in dropoff_mapping}
    dropoffs_dict = defaultdict(list)
    for h in convert_locations_to_indices(list_of_homes, list_of_locations):
        minValue = float('inf')
        minVertex = mapping[start]
        for i in traversal:
            if distances[h][i] < minValue:
                minValue = distances[h][i]
                minVertex = i
        dropoffs_dict[minVertex].append(h)
    dropoffs_dict = {key: dropoffs_dict[key] for key in dropoffs_dict}
    return traversal, dropoffs_dict

