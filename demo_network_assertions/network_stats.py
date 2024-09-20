import pandas as pd
import statistics as stats
from matplotlib import pyplot as plt
import numpy as np
import csv

# load data 
network_type = 'signature_shuffling'
edge_dir = f"/Users/anna/Projects/KG_UI/build_TF_network/filter_assertions_out/benchmarking/{network_type}"
dn_edges = pd.read_csv(f"{edge_dir}/Transcription Factor.downregulates.Transcription Factor.edges.csv")
up_edges = pd.read_csv(f"{edge_dir}/Transcription Factor.upregulates.Transcription Factor.edges.csv")
nodes = pd.read_csv(f"{edge_dir}/Transcription Factor.nodes.csv")

all_edges = pd.concat([up_edges, dn_edges], ignore_index=True)

# find number of edges in each file
n_up_edges = up_edges.shape[0]
n_dn_edges = dn_edges.shape[0]
total_edges = all_edges.shape[0]

if n_up_edges + n_dn_edges != total_edges:
    print("Error!")

# number of source and target nodes
total_srcs = len(all_edges['source'].value_counts(dropna=True))
total_targs = len(all_edges["target"].value_counts(dropna=True))
total_nodes = len(set(all_edges['source'] + all_edges['target']))

# number of out per node is the number of times it is an up or down source
unique_sources = set(all_edges["source"])
avg_out = total_edges/total_srcs

# number of in links per node is the number of times its an up or down target
unique_targets = set(all_edges["target"])
avg_in = sum(all_edges["target"].value_counts())/total_targs

unique_nodes = unique_sources | unique_targets
# histogram
def counts_histogram(direction, fig_size = (10,6), num_bins = 19):
    if direction == "in":
        counts = all_edges['target'].value_counts()
    else:
        counts = all_edges['source'].value_counts()

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



# average total links per node is the number of times it is either
total_in = (total_edges + total_edges)/len(unique_sources | unique_targets)

# number of self loops is the number of times the source and target are the same 
all_edges['self_loop'] = all_edges.apply(lambda row: 1 if row['source'] == row['target'] else 0, axis=1)
total_loops = all_edges['self_loop'].sum()

def find_loops(edges):
    reversed = edges.rename(columns={'source': 'target', 'target': 'source'})
    merged = pd.merge(edges, reversed, on=['source', 'relation', 'target'])
    merged = merged[merged['source'] != merged['target']]
    merged['pair'] = merged.apply(lambda row: tuple(sorted((row['source'], row['target']))), axis=1)
    return merged['pair'].drop_duplicates().shape[0]

up_loops = find_loops(up_edges)
dn_loops = find_loops(dn_edges)

# print results
with open(f'./demo_network_assertions/network_stats/{network_type}_network_stats.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['Total nodes', len(unique_nodes)])
    writer.writerow(['Unique source nodes', total_srcs])
    writer.writerow(['Unique target nodes', total_targs])
    writer.writerow(['Total edges', total_edges])
    writer.writerow(['Number of up edges',n_up_edges])
    writer.writerow(['Number of dn edges',n_dn_edges])
    writer.writerow(['Avg out links per node',avg_out])
    writer.writerow(['Avg in links per node',avg_in])
    writer.writerow(['Avg total links per node', total_in])
    writer.writerow(['Number of self loops',total_loops])
    writer.writerow(['Number of upregulated two-item loops',up_loops])
    writer.writerow(['Number of downregulated two-item loops', dn_loops])

counts_histogram("in")
#plt.show()
counts_histogram("out")
#plt.show()