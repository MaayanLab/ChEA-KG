import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

# load data 
def load_network_edges(network_type, edge_list_dir="./filtered_edge_list"):
    network = pd.read_csv(f"{edge_list_dir}/{network_type}/edge_list_filtered.csv", usecols=['source','target','relation'])
    return {
        'all edges': network, 
        'dn edges': network[network['relation']=='-'], 
        'up edges': network[network['relation']=='+'], 
        'all nodes': pd.concat([network['source'],network['target']]).unique()
        }

def n_nodes(all_edges):
    total_srcs = len(set(all_edges['source']))
    total_targs = len(set(all_edges["target"]))
    return {
        'sources':total_srcs,
        'targets':total_targs,
    }

def avg_node_degree(all_edges, node_type):
    return len(all_edges)/len(set(all_edges[node_type]))

# histogram
def plot_degree_counts_histo(direction, edge_list, fig_size = (10,6), num_bins = 19):
    if direction == "in":
        counts = edge_list['target'].value_counts()
    else:
        counts = edge_list['source'].value_counts()

    plt.figure(figsize=fig_size)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.hist(counts, bins = num_bins, edgecolor ='black')
    # plt.yscale('log')
    plt.ylabel('Frequency', fontsize=16)

    if direction == "in":
        plt.xlabel('Target relationships per node', fontsize=16)
        ticks = np.arange(2, 21, 2)
        plt.xticks(ticks)
    else:
        plt.xlabel('Source relationships per node', fontsize=16)

# number of self loops is the number of times the source and target are the same 
def n_self_loops(all_edges):
    all_edges['self_loop'] = all_edges.apply(lambda row: 1 if row['source'] == row['target'] else 0, axis=1)
    return all_edges['self_loop'].sum()

def n_feedback_loops(edge_type):
    reversed = edge_type.rename(columns={'source': 'target', 'target': 'source'})
    merged = pd.merge(edge_type, reversed, on=['source', 'relation', 'target'])
    merged = merged[merged['source'] != merged['target']]
    merged['pair'] = merged.apply(lambda row: tuple(sorted((row['source'], row['target']))), axis=1)
    return merged['pair'].drop_duplicates().shape[0]

def all_network_stats(network_type):
    network = load_network_edges(network_type)
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
    
    # Save as csv - 
    # df.T.to_csv(f'{output_dir}/{network_type}/network_statistics.csv')