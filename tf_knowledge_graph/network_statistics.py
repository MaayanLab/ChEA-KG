import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

# load data 
def load_network_edges(edge_list_dir):

    """
    Loads edges from a CSV where each row contains source,target,[direction or relation]
    """

    network = pd.read_csv(edge_list_dir, usecols=[0, 1, 2])

    if network.columns[2] == 'direction':
        network.rename(columns={'direction':'relation'}, inplace=True)
        
    return {
        'all edges': network, 
        'dn edges': network[network['relation']=='-'], 
        'up edges': network[network['relation']=='+'], 
        'all nodes': pd.concat([network['source'],network['target']]).unique()
        }


def n_nodes(all_edges):

    """"
    finds the number of unique source and target nodes
    """

    total_srcs = len(set(all_edges['source']))
    total_targs = len(set(all_edges["target"]))
    return {
        'sources':total_srcs,
        'targets':total_targs,
    }


def avg_node_degree(all_edges, node_type):

    """
    calculates the average node degree
    """

    return len(all_edges)/len(set(all_edges[node_type]))


def plot_connectivity_distrib(edge_list_file, output, fig_size = (6,5)):

    """
        plots the connectivity distribution using log-scaled histogram of the relative frequency
        edge_list_file: a file with a list of edges, must have column named 'source' and 'target'
        output: the directory where to save the images 
    """

    network = pd.read_csv(edge_list_file, usecols=['source', 'target'])

    # Get the frequency of each node as either a source or a target in an edge
    out_counts = network['source'].value_counts()
    in_counts = network['target'].value_counts()
    out_bins = max(out_counts)//50

    # OUTDEGREE
    plt.figure(figsize=fig_size, dpi=300)
    plt.hist(out_counts, bins = out_bins, edgecolor ='none', color='black', 
             weights = np.ones_like(out_counts) / len(out_counts))
    plt.yscale('log')
    
    plt.ylabel('Relative frequency', fontsize=14)
    plt.xlabel('Node out-degree', fontsize=14)

    plt.tight_layout()
    plt.savefig(f"{output}/img/out_degree_unfiltered.png")
    plt.show()

    # INDEGREE  
    plt.figure(figsize=fig_size, dpi=300)
    plt.hist(in_counts, bins = out_bins, edgecolor ='none', color='black', 
             weights = np.ones_like(in_counts) / len(in_counts))
    plt.yscale('log')
    
    plt.ylabel('Relative frequency', fontsize=14)
    plt.xlabel('Node in-degree', fontsize=14)
    plt.xlabel('Node out-degree', fontsize=14)

    plt.tight_layout()
    plt.savefig(f"{output}/img/in_degree_unfiltered.png")
    plt.show()
    


def n_self_loops(all_edges):

    """
    find the number of self loops
    """

    all_edges['self_loop'] = all_edges.apply(lambda row: 1 if row['source'] == row['target'] else 0, axis=1)
    return all_edges['self_loop'].sum()


def n_feedback_loops(edge_type):

    """
    return the number of feedback loops
    edge_type: specifies positive edges or negative edges
    """

    reversed = edge_type.rename(columns={'source': 'target', 'target': 'source'})
    merged = pd.merge(edge_type, reversed, on=['source', 'relation', 'target'])
    merged = merged[merged['source'] != merged['target']]
    merged['pair'] = merged.apply(lambda row: tuple(sorted((row['source'], row['target']))), axis=1)
    return merged['pair'].drop_duplicates().shape[0]


def all_network_stats(edge_list_file, save = False, output = None):

    """
    calculate all network statistics and print to the screen
    edge list file: the name of an edge list
    output: where to optionally save the network stats as a csv
    """

    network = load_network_edges(edge_list_file)
    all_edges = network['all edges']
    N_nodes = n_nodes(all_edges)

    stats = {
        'Total nodes':network['all nodes'].shape[0],
        'Unique source nodes':N_nodes['sources'],
        'Unique target nodes':N_nodes['targets'],
        'Total edges':all_edges.shape[0],
        'Number of up edges':network['dn edges'].shape[0],
        'Number of dn edges':network['up edges'].shape[0],
        'Avg out links per node':avg_node_degree(all_edges, 'target'),
        'Avg in links per node':avg_node_degree(all_edges, 'source'),
        'Avg total links per node':all_edges.shape[0] / network['all nodes'].shape[0],
        'Number of self loops':n_self_loops(all_edges),
        'Number of upregulation feedback loops':n_feedback_loops(network['up edges']),
        'Number of downregulation feedback loops':n_feedback_loops(network['dn edges'])
    }

    df = pd.DataFrame([stats])
    print(df.T)
    if save == True and output != None:
        df.T.to_csv(f'{edge_list_file}/network_statistics.csv')
    elif save == True:
        print("Must provide output directory to save")