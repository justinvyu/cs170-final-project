import numpy as np
import random
from student_utils import adjacency_matrix_to_graph
import matplotlib.pyplot as plt
import networkx as nx

def init_adj_matrix(num_vertices):
    return [
        ['x' for _ in range(num_vertices)]
        for _ in range(num_vertices)
    ]

def create_random_graph():
    pass

def create_branching_graph(num_locations,
                           max_branching_factor=3,
                           branch_prob=0.25):
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
    
    return adj, vertex_positions

GRAPH_TYPES = {
    'random': create_random_graph,
    'branching': create_branching_graph,
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

    adj, pos = GRAPH_TYPES[args.graph_type](args.num_locations)
    G, message = adjacency_matrix_to_graph(adj)

    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, with_labels=True, pos=pos)
    plt.show()