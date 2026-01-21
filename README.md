## Molecular Graph Comparison using NAUTY

# Objective
This project compares molecular structures by modeling molecules as graphs and testing graph isomorphism using the NAUTY library. Two molecules are considered identical if their molecular graphs are isomorphic.

# Dependencies

1. Python 3

2. NAUTY (dreadnaut, dretog, labelg)

3. curl, gunzip

# Data Source
Molecular data are retrieved from the ChEBI database in SDF format.

# Pipeline

. Download the ChEBI SDF file (once)

. Extract molecules by ChEBI ID

. Convert MOL to graph format (.dre)

. Convert .dre to graph6

. Canonicalize graphs using labelg

. Compare canonical graphs

# Usage
To compare two molecules:

./compare_graphs.sh 27732 15373


Output indicates whether the two molecules are isomorphic or not.

# Main Scripts

. parser.py: extracts molecules from SDF and generates .mol and .dre files

. compare_graphs.sh: performs canonicalization and graph comparison using NAUTY

Theory
Molecules are represented as undirected graphs where vertices correspond to atoms and edges to chemical bonds. Structural equivalence is reduced to a graph isomorphism problem
