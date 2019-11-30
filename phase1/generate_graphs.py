import numpy as np
import random
from student_utils import adjacency_matrix_to_graph, is_metric
import matplotlib.pyplot as plt
import networkx as nx
import itertools
from phase1.subgraph import Subgraph, join_subgraphs

def init_adj_matrix(num_vertices):
    return [
        ['x' for _ in range(num_vertices)]
        for _ in range(num_vertices)
    ]

def create_random_graph(num_vertices, sparsity=.5):
    assert num_vertices > 1
    G = create_random_tree(num_vertices)
    num_edges = num_vertices - 1
    total_edges = (1 - sparsity) * num_vertices * (num_vertices - 1)
    remaining_edges = [pair for pair in itertools.combinations(G.nodes(), 2)
           if not G.has_edge(*pair) and pair[0] != pair[1]]
    while num_edges < total_edges and remaining_edges:
        rand_idx = random.randint(0, len(remaining_edges) - 1)
        new_edge = remaining_edges.pop(rand_idx)
        shortest_path = sum(nx.shortest_path(G, *new_edge))
        weight = random.randint(1, shortest_path - 1)
        G.add_edge(*new_edge, weight=weight)
        if not is_metric(G):
            G.remove_edge(*new_edge)
        num_edges += 1
    sample_size = num_vertices // 4 if num_vertices //4 >= 2 else 2
    sample = np.random.choice(num_vertices, size=sample_size, replace=False)
    np.random.shuffle(sample)
    return Subgraph(G, sample[0:len(sample)//2].tolist(), sample[len(sample)//2:].tolist())

def create_random_tree(num_vertices, scale=100, offset=3):
    adj = (np.random.rand(num_vertices, num_vertices) * scale + offset).astype(np.uint32)
    G, message = adjacency_matrix_to_graph(adj)
    G = nx.minimum_spanning_tree(G)
    return G

def create_cycle_graph(num_vertices, scale=30):
    assert num_vertices > 1
    adj = [[0 for i in range(num_vertices)] for j in range(num_vertices)]
    path_weight = 0
    for i in range(1, num_vertices):
        weight = random.randint(1, scale)
        adj[i - 1][i] = weight
        path_weight += weight
    adj[num_vertices - 1][0] = random.randint(1, path_weight - 1)
    G, message = adjacency_matrix_to_graph(adj)
    sample_size = num_vertices // 4 if num_vertices //4 >= 2 else 2
    sample = np.random.choice(num_vertices, size=sample_size, replace=False)
    np.random.shuffle(sample)
    return Subgraph(G, sample[0:len(sample)//2].tolist(), sample[len(sample)//2:].tolist())

def create_diamond_graph(num_vertices, scale=30):
    assert num_vertices % 4 == 0
    G = create_cycle_graph(num_vertices, scale)._G
    side = num_vertices // 4
    corners1 = 0
    corners2 = side
    corners3 = side * 2
    corners4 = side * 3
    while corners1 + 1 != corners2 and corners3 + 1 != corners4:
        corners1 += 1
        corners3 += 1
        if random.randint(0, 1) == 1:
            shortest_path = sum(nx.shortest_path(G, corners1, corners3))
            weight = random.randint(1, shortest_path - 1)
            G.add_edge(corners1, corners3, weight=weight)
            if not is_metric(G):
                G.remove_edge(corners1, corners3)
    return Subgraph(G, [corners1], [corners3])

def create_branching_graph(num_locations,
                           max_branching_factor=3,
                           branch_prob=0.5):
    """
    Input:
        num_locations: Number of vertices in this subgraph.
        max_branching_factor: Maximum number of branches a node can spit into,
                              where the number of branches will be randomly
                              decided between [2, max_branching_factor].
        branch_prob: Probability of any node branching, in [0, 1].
    Output:
        adj: branching subgraph adjacency matrix
        s: source vertex (0)
    """
    assert max_branching_factor >= 2, (
        f'Max branching factor = {max_branching_factor}, but should be >= 2')
    assert branch_prob >= 0 and branch_prob <= 1, (
        f'Branch probability = {branch_prop}, but should be within [0, 1]')

    # TODO: Come up with random weight generation
    def get_random_weight():
        return 1

    adj = init_adj_matrix(num_locations)
    queue = [0] # 0 is the source
    next_vertex = 1

    x_pos = 0
    vertex_positions = {}
    while next_vertex < num_locations:
        for y_pos in range(len(queue)):
            v = queue.pop(0)
            vertex_positions[v] = (x_pos, y_pos)
            if next_vertex >= num_locations:
                break
            # Add the next vertex, regardless of branch
            adj[v][next_vertex] = adj[next_vertex][v] = get_random_weight()
            queue.append(next_vertex)
            next_vertex += 1
            # Add extra branches with P(branch) = branch_prob
            if random.random() < branch_prob:
                num_branches = random.randint(1, max_branching_factor - 1)
                for branch_num in range(num_branches):
                    if next_vertex >= num_locations:
                        break
                    adj[v][next_vertex] = adj[next_vertex][v] = get_random_weight()
                    queue.append(next_vertex)
                    next_vertex += 1
        x_pos += 1
    
    G, message = adjacency_matrix_to_graph(adj)
    inp = [0]
    out = []
    for i in range(num_locations):
        if G.degree[i] == 1 and i > 0:
            out.append(i)
    return Subgraph(G, inp, out)

GRAPH_TYPES = {
    'random': create_random_graph,
    'branching': create_branching_graph,
    'cycle': create_cycle_graph,
    'diamond': create_diamond_graph
}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('num_locations', type=int)
    parser.add_argument('--graph-type',
                        type=str,
                        default='branching',
                        choices=list(GRAPH_TYPES.keys()))
    args = parser.parse_args()

    G = GRAPH_TYPES[args.graph_type](args.num_locations)

    pos = nx.kamada_kawai_layout(G)
    import ipdb; ipdb.set_trace()
    #nx.draw(G, with_labels=True, pos=pos)
    #labels = nx.get_edge_attributes(G,'weight')
    #nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
    #plt.show()
