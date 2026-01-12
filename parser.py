import os

def parse_mol(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    counts_line = lines[3].strip()
    if not counts_line:
        return [], []
        
    try:
        num_atoms = int(counts_line[0:3].strip())
        num_bonds = int(counts_line[3:6].strip())
    except ValueError:
        return [], []

    atoms = []
    bonds = []

    atom_start = 4
    atom_end = atom_start + num_atoms
    for i in range(atom_start, atom_end):
        line = lines[i]
        symbol = line[31:34].strip()
        atoms.append(symbol)

    bond_start = atom_end
    bond_end = bond_start + num_bonds
    for i in range(bond_start, bond_end):
        line = lines[i]
        a1 = int(line[0:3])
        a2 = int(line[3:6])
        bond_type = int(line[6:9])
        bonds.append((a1, a2, bond_type))

    return atoms, bonds

def write_dreadnaut(mol_filename):
    """
    Génère un fichier .dre valide pour nauty/dretog.
    """
    if not os.path.exists(mol_filename):
        print(f"Erreur : {mol_filename} introuvable.")
        return

    dre_filename = mol_filename.rsplit('.', 1)[0] + ".dre"
    atoms, bonds = parse_mol(mol_filename)
    
    if not atoms:
        print(f"Erreur de lecture pour {mol_filename}")
        return

    num_atoms = len(atoms)

    # Construire la liste des voisins
    neighbors = [[] for _ in range(num_atoms)]
    for a1, a2, _ in bonds:
        neighbors[a1 - 1].append(a2 - 1)
        neighbors[a2 - 1].append(a1 - 1)

    # Écriture du fichier .dre
    with open(dre_filename, "w") as f:
        f.write(f"n={num_atoms}\n")
        f.write("g\n")
        
        for i, nbrs in enumerate(neighbors):
            nbrs_str = " ".join(str(n) for n in sorted(nbrs))
            f.write(f"{i}: {nbrs_str}\n")
        
        f.write(".\n")  # Fin du fichier

    print(f"Fichier généré : {dre_filename}")

# ---- Exemple ---- #
write_dreadnaut("CHEBI_16040.mol")
write_dreadnaut("CHEBI_55502.mol")
