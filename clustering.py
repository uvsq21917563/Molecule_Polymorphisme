
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.DataStructs import TanimotoSimilarity
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

import numpy as np

# --- 1. Charger des molécules à partir d'un fichier SDF --- #
def load_molecules(sdf_file, max_mol=None):
    suppl = Chem.SDMolSupplier(sdf_file, sanitize=False)  # désactive le sanitize initial
    mols = []
    for mol in suppl:
        if mol is None:
            continue
        try:
            Chem.SanitizeMol(mol)  # tente de "nettoyer" la molécule
            mols.append(mol)
        except:
            continue  # ignore les molécules impossibles
        if max_mol and len(mols) >= max_mol:
            break
    return mols


# --- 2. Calculer les fingerprints pour Tanimoto --- #
def calc_fingerprints(mols, radius=2, nBits=2048):
    fps = []
    for mol in mols:
        try:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
            fps.append(fp)
        except:
            fps.append(None)  # ou ignorer
    # supprimer les None
    mols = [mol for mol, fp in zip(mols, fps) if fp is not None]
    fps = [fp for fp in fps if fp is not None]
    return fps, mols


# --- 3. Calculer les descripteurs physico-chimiques --- #
def calc_descriptors(mols):
    descriptors = []
    valid_mols = []
    for mol in mols:
        try:
            desc = [
                Descriptors.MolWt(mol),
                Descriptors.MolLogP(mol),
                Descriptors.NumRotatableBonds(mol),
                Descriptors.NumHDonors(mol),
                Descriptors.NumHAcceptors(mol)
            ]
            descriptors.append(desc)
            valid_mols.append(mol)
        except:
            continue
    return np.array(descriptors), valid_mols


# --- 4. Calcul de la matrice de distance --- #
def tanimoto_distance_matrix(fps):
    n = len(fps)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = 1 - TanimotoSimilarity(fps[i], fps[j])
    return dist_matrix

def euclidean_distance_matrix(desc):
    return squareform(pdist(desc, metric='euclidean'))

# recuperer les id et noms des molecules
def get_chebi_id(mol):
    """Récupère l'ID ChEBI d'une molécule"""
    if mol.HasProp('ChEBI ID'):
        return mol.GetProp('ChEBI ID')
    elif mol.HasProp('_ChEBI_ID'):
        return mol.GetProp('_ChEBI_ID')
    else:
        return str(mol.GetIdx())  # fallback sur l'index

def get_chebi_name(mol):
    """Récupère le nom ChEBI"""
    if mol.HasProp('ChEBI NAME'):
        return mol.GetProp('ChEBI NAME')
    elif mol.HasProp('_Name'):
        return mol.GetProp('_Name')
    else:
        return f"Mol_{mol.GetIdx()}"


# --- 5. Clustering hiérarchique et affichage dendrogramme --- #
def cluster_and_plot(dist_matrix, labels, method='average', title='Clustering'):
    Z = linkage(squareform(dist_matrix), method=method)
    plt.figure(figsize=(20, 10))
    dendrogram(Z, labels=labels)
    plt.title(title)
    plt.show()

# --- 6. Exemple d'utilisation --- #
if __name__ == "__main__":
    sdf_file = "chebi.sdf"  # ou ton fichier

mols = load_molecules(sdf_file, max_mol=50)  # plus pour test
#labels = [f"CHEBI_{get_chebi_id(mol)}" for mol in mols]
labels = [f"{get_chebi_id(mol)}" for mol in mols]


fps, mols = calc_fingerprints(mols)
tan_dist = tanimoto_distance_matrix(fps)
cluster_and_plot(tan_dist, labels=labels, title='Clustering Tanimoto')

desc, mols_desc = calc_descriptors(mols)
eu_dist = euclidean_distance_matrix(desc)
cluster_and_plot(eu_dist, labels=labels, title='Clustering Descripteurs')