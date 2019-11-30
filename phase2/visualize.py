import sys
sys.path.append('..')

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from student_utils import adjacency_matrix_to_graph
from solver_utils import parse_input

def plot_graph(filepath,
               layout_style=nx.spring_layout,
               show_labels=True,
               show_edge_weights=False):
    (num_locations,
     num_houses,
     location_names,
     house_names,
     source,
     adj) = parse_input(filepath)
    
    G, _ = adjacency_matrix_to_graph(adj)
    
    plt.figure(figsize=(10,10))
    pos = layout_style(G)
    colormap = [
        ('yellow' if str(i) in house_names else 'red')
        for i in range(num_locations)
    ]
    source_index = location_names.index(source)
    colormap[source_index] = 'blue'

    nx.draw(G, pos=pos, node_color=colormap, with_labels=show_labels)
    if show_edge_weights:
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels)
        
    plt.show()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', type=str, help='Path to the .in file')
    args = parser.parse_args() 
    
    plot_graph(args.filepath)
