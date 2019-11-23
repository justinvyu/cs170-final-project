from generate_graphs import (
    create_random_graph,
    create_branching_graph,
    create_cycle_graph,
    create_diamond_graph)
from subgraph import join_subgraphs
import random
import os
from utils import write_to_file
from student_utils import is_metric

def generate_small():
    return create_branching_graph(50, 3, .5)

def generate_bigger(size):
    func = [create_random_graph, create_branching_graph, create_cycle_graph, create_diamond_graph]
    limit = size
    graphs = []
    while limit > 0:
        indx = random.randint(0, 3)
        if indx == 0:
            num_verts = random.randint(min(5, limit), min(10, limit))
        if indx == 1:
            num_verts = random.randint(min(15, limit), min(45, limit))
        if indx == 2:
            num_verts = random.randint(min(8, limit), min(10, limit))
        if indx == 3:
            num_verts = random.randint(min(8, limit), min(10, limit))
            remainder = num_verts % 4
            num_verts -= remainder
        num_verts = min(num_verts, limit)
        graphs.append(func[indx](num_verts))
        limit -= num_verts
        print(limit)
    return join_subgraphs(graphs)

if __name__ == '__main__':
    G = generate_bigger(200)
    print(is_metric(G._G))
    G.draw()

def select_houses(G, num_houses):
    sample = np.random.choice(len(G), size=num_houses, replace=False)


def write_input_to_file(filepath, G, H, source):
    """
    filepath: Path to save the input
    G: NetworkX graph of the final input
    H: list of houses referenced by the vertex identifier
    source: vertex identifier of the source node
    """
    # assert source in G, 'Source vertex must be in the graph'

    def list_as_str(lst):
        return [str(el) for el in lst]

    num_vertices = len(G)
    write_to_file(filepath, f'{num_vertices}\n')
    num_houses = len(H)
    write_to_file(filepath, f'{num_houses}\n', append=True)
    write_to_file(filepath, " ".join(list_as_str(G.nodes())) + '\n', append=True)
    write_to_file(filepath, " ".join(list_as_str(H)) + '\n', append=True)
    write_to_file(filepath, f'{source}\n', append=True)
    adj = graph_to_adjacency_matrix(G)
    for i, row in enumerate(adj):
        write_to_file(filepath,
            " ".join(list_as_str(row)) + ('\n' if i < len(adj) - 1 else ''),
            append=True)

def graph_to_adjacency_matrix(G):
    adj = [['x' for _ in range(len(G))] for _ in range(len(G))]
    for edge in G.edges(data=True):
        u, v, data = edge
        adj[u][v] = adj[v][u] = data['weight']
    return adj

if __name__ == '__main__':
    from generate_graphs import create_branching_graph
    G = create_branching_graph(10)
    H = [2, 4, 6]
    source = 0
    fp = './test.in'
    write_input_to_file(fp, G, H, source)
