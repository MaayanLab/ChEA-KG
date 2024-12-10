# ChEA-KG: Exploring a Novel Human Gene Regulatory Network

## **The ChEA-KG GRN**
***Nodes***
* Nodes in the ChEA-KG are human transcription factors cataloged by [ChEA3](https://maayanlab.cloud/chea3/). 
* Each node is associated with an **id, label**, and **URI** that points to the NCBI gene page for that gene.

***Edges***
* Edges in the GRN indicate regulatory relationships between source and target TFs, inferred from enrichment analysis.  
* There are two edge types: 
    1. <span style="color: red;">Red</span> plungers indicate downregulation
    2. <span style="color: green;">Green</span> arrows inidcate upregulation

### **Searching the ChEA-KG GRN**
Click and drag on any node to move it. 

#### One-term search
Generate a subnetwork of itneractions between a single transcription factor and its neighboring nodes by inputting the gene symbol for a transcription factor into the search bar under "Start with". Type in the gene symbol. If it exists in the network, it will be shown in the autocomplete menu. Click on the matching name to view the results. 

#### Subgraph search
Generate a subnetwork with a given number of relationships by toggling the "End Node" switch. Leave the "End with" field **blank**. Control the size of the subnetwork using the slider above the network view. 

#### Two-term search
The two-term search generates a shortest path between two transcription factor nodes. Enter a starting transcription factor in the "Start with" field. Toggle the "End Node" switch, then input a desired end node in the "End with" field. The result displays a shorest path between the two nodes. In the case where there is a tie for a shortest path length, all paths of that length are shown. 

### ** Interacting with the network ** 
The toolbar above the network view provides several buttons to further interact with the network. From left to right, these are Size, Full-screen, Network view, Table view, Save subnetwork, Download graph as an image file, Show tooltip, Switch graph layout, Show edge labels, and Show legend.  

To move a node in the network view, click and drag. 

#### Adjust the network view:
The toolbar above the network view provides the following buttons to further interact with the network, from left to right: 
* Adjust subnetwork size: Adjust the size slider to limit the number of relationships displayed for that network
* Full-screen: Click the full-screen button to view the network search page in full-screen
* Enable the tooltip: The tooltip displays the ID, label, and URI for each node when the mouse hovers over a node in the network. It also provides options to remove or expand a ndoe.  
* Remove or expand a node: With the tooltip enabled, hover over the node of interest and click on the remove or expand buttons. 
* Network and table view: Toggle between network and table view by clicking on their respective buttons
* Switch graph layout: Switch between force-directed, geometric, or hierarchical graph layouts. 
* Show edge labels: Display the edge labels ("upregulates", "downregulates") over the edges
* Show legend: Show the legend. An additional toolbar button is displayed that adjusts the size of the legend when clicked. 

#### Download the network: 
* Save subnetwork: Save the subnetwork to a file. This produces two files: 
    - nodes.csv has the fields [id, label, kind, uri, color]
    - edges.csv has the  fields [source, target, relation, source_label, target_label, kind, p_value, z_score]
* Download graph as an image file: Save a PNG, JPG, or SVG image of the network view

## **Enrichment analysis with ChEA-KG**
The enrichment analysis page provides an option to visualize a subnetwork of the GRN based on ChEA3 enrichment analysis results. 

### Enrichment analysis subnetwork
The subnetwork returned by this feature contains transcription factors with the highest integrated mean rank for that gene set. By default, the top 10 ranked TFs are returned. The ChEA3 integrated mean rank is calculated from the average rank across six libraries: Enrichr Queries, GTEx Coexpression, ARCHS4 Coexpression, ENCODE ChIP-seq, Literature ChIP-seq, and ReMap ChIP-seq. For more information on how the ChEA3 Integrated Mean Rank is calculated, visit the [ChEA3 website](https://maayanlab.cloud/chea3/). 

#### Enrichment analysis search parameters:
There are three advanced search options that can be adjusted by toggling "Advanced Options". 
1. Minimum libraries: This filters out nodes from the enrichment results if they occur in fewer than the specified number of ChEA3 libraries (maximum of 6)
2. Maximum edge p-value: Specify the maximum p-value of an edge. 
3. Specify number of nodes: Specify how many top ranked nodes. 

#### Perform a query:
To perform a query, input a list of newline-separated Entrez gene symbols into the text box. Alternatively, click "try an example" to use an example gene set. Add a description under the "Description" field. Adjust the advanced options as necessary. Click submit. 