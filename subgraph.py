import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
from generate_graphs import create_random_graph, create_branching_graph

def get_weights(G):
    return [e[2]['weight'] for e in G.edges(data=True)]

class Subgraph:
    def __init__(self, G, input_vertices, output_vertices):
        """
        G: NetworkX-wrapped of the underlying graph
        input_vertices: list of >= 1 vertices that other components can to
        output_vertices: list of >= 1 vertices that other components can connect to
        """
        self._G = G
        assert isinstance(input_vertices, list) and isinstance(output_vertices, list), (
            'Input and output vertices need to be specified as lists of >= 1 vertex'
        )
        self.input_vertices = input_vertices
        self.output_vertices = output_vertices

    def draw(self):
        nx.draw(self._G)
        plt.show()

    @classmethod
    def join(cls, subgraph1, subgraph2, connection_density=0.25):
        """
        connection_density: max_connections = connection_density *
                            min(|subgraph1.output_vertices|, |subgraph.input_vertices|)
                            Sample the number of connections between [1, max_connections]
        """
        G = subgraph1._G
        H = subgraph2._G
        H = nx.relabel_nodes(H, lambda x: x + len(G))
        
        H_input_vertices = [v + len(G) for v in subgraph2.input_vertices]
        output_vertices = [v + len(G) for v in subgraph2.output_vertices]
        merged_graph = nx.compose(G, H)

        # Add edges between subgraph1.output_vertices and subgraph2.input_vertices
        max_connections = int(connection_density * min(
            len(subgraph1.output_vertices), len(subgraph2.input_vertices)))
        num_connections = random.randint(1, max(max_connections, 1))
        num_edges_added = 0

        max_weight_edge = max(get_weights(merged_graph)) 
        left, right = subgraph1.output_vertices.copy(), H_input_vertices 

        while num_edges_added < num_connections:
            rand_idx_left, rand_idx_right = (
                np.random.randint(len(left)),
                np.random.randint(len(right)))
            u, v = left.pop(rand_idx_left), right.pop(rand_idx_right)
            merged_graph.add_edge(u, v, weight=max_weight_edge)
            num_edges_added += 1

        return Subgraph(
            G=merged_graph,
            input_vertices=subgraph1.input_vertices,
            output_vertices=output_vertices)
 
def join_subgraphs(subgraphs):
    assert subgraphs, 'List of subgraphs cannot be empty'
    if len(subgraphs) == 1:
        return subgraphs[0]
    merged = subgraphs[0]
    for i in range(1, len(subgraphs)):
        subgraph = subgraphs[i]
        merged = Subgraph.join(merged, subgraph)
    return merged
