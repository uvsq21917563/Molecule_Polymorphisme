#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser SDF → fichiers .mol et .dre pour NAUTY

3 modes :
1. Tout générer
2. Générer les x premières molécules
3. Générer une seule molécule via son ChEBI_ID

Usage :
    python3 parser.py chemin_fichier.sdf [--all | --first X | --chebi ID]
"""

import argparse
import os

ATOM_TYPES = {}      # symbole chimique-> id de partition
BOND_TYPES = {       # MOL bond type -> label
    1: "SINGLE",
    2: "DOUBLE",
    3: "TRIPLE",
    4: "AROM"
}


# ------------------------- Parser MOL ------------------------- #
def parse_mol_lines(lines):
    """Parse les lignes d'une molécule MOL et retourne atoms et bonds"""
    counts_line = lines[3].strip()
    num_atoms = int(counts_line[0:3])
    num_bonds = int(counts_line[3:6])

    atoms = []
    bonds = []

    # Atom block
    atom_start = 4
    atom_end = atom_start + num_atoms
    for i in range(atom_start, atom_end):
        line = lines[i]
        symbol = line[31:34].strip()
        atoms.append(symbol)

    # Bond block
    bond_start = atom_end
    bond_end = bond_start + num_bonds
    for i in range(bond_start, bond_end):
        line = lines[i]
        a1 = int(line[0:3])
        a2 = int(line[3:6])
        bond_type = int(line[6:9])
        bonds.append((a1, a2, bond_type))

    return atoms, bonds

# --------------------- Fichier dreadnaut ---------------------- #
def write_dreadnaut(atoms, bonds, dre_filename):
    """
    Graphe biparti :
    - sommets 0..A-1 : atomes
    - sommets A..A+B-1 : liaisons
    """

    atom_count = len(atoms)
    bond_count = len(bonds)
    total_vertices = atom_count + bond_count

    neighbors = [[] for _ in range(total_vertices)]

    atom_labels = []
    bond_labels = []

    # --- Labels atomes ---
    for sym in atoms:
        atom_labels.append(sym)

    # --- Sommets liaisons ---
    for i, (a1, a2, bond_type) in enumerate(bonds):
        bond_vertex = atom_count + i
        a1 -= 1
        a2 -= 1

        neighbors[a1].append(bond_vertex)
        neighbors[a2].append(bond_vertex)
        neighbors[bond_vertex].extend([a1, a2])

        bond_labels.append(BOND_TYPES.get(bond_type, "SINGLE"))

    # --- Construire partitions ---
    partitions = {}

    for i, label in enumerate(atom_labels + bond_labels):
        partitions.setdefault(label, []).append(i)

    # --- Écriture .dre ---
    with open(dre_filename, "w") as f:
        f.write(f"n={total_vertices}\n")
        f.write("g\n")
        for i, nbrs in enumerate(neighbors):
            f.write(f"{i}: {' '.join(map(str, sorted(nbrs)))};\n")
        f.write(".\n")

        # Partitions (labels)
        f.write("c\n")
        blocks = []
        for block in partitions.values():
            blocks.append(" ".join(map(str, block)))
        f.write(" | ".join(blocks) + "\n")

        f.write("q\n")


# ----------------------- Parcours SDF ------------------------ #
def process_sdf(sdf_file, mode, param=None):
    """Parcours un fichier SDF et génère les fichiers .mol et .dre selon mode"""
    if not os.path.exists(sdf_file):
        print(f"Erreur : {sdf_file} introuvable")
        return

    mol_lines = []
    count = 0
    found = False

    with open(sdf_file, "r") as f:
        for line in f:
            mol_lines.append(line)
            if line.strip() == "$$$$":
                count += 1
                # Récupère le ChEBI_ID
                chebi_id_line = [l for l in mol_lines if "CHEBI:" in l]
                chebi_id = None
                if chebi_id_line:
                    chebi_id = chebi_id_line[0].strip().split(":")[-1]

                # ---------------- Mode 1 : Tout ---------------- #
                if mode == "all":
                    if chebi_id:
                        mol_filename = f"CHEBI_{chebi_id}.mol"
                        dre_filename = f"CHEBI_{chebi_id}.dre"
                        with open(mol_filename, "w") as mf:
                            mf.writelines(mol_lines)
                        atoms, bonds = parse_mol_lines(mol_lines)
                        write_dreadnaut(atoms, bonds, dre_filename)
                        print(f"[{count}] {mol_filename} / {dre_filename} généré")

                # ---------------- Mode 2 : premières X ---------------- #
                elif mode == "first":
                    if count <= param:
                        if chebi_id:
                            mol_filename = f"CHEBI_{chebi_id}.mol"
                            dre_filename = f"CHEBI_{chebi_id}.dre"
                            with open(mol_filename, "w") as mf:
                                mf.writelines(mol_lines)
                            atoms, bonds = parse_mol_lines(mol_lines)
                            write_dreadnaut(atoms, bonds, dre_filename)
                            print(f"[{count}] {mol_filename} / {dre_filename} généré")

                # ---------------- Mode 3 : ChEBI_ID ---------------- #
                elif mode == "chebi":
                    if chebi_id == str(param):
                        mol_filename = f"CHEBI_{chebi_id}.mol"
                        dre_filename = f"CHEBI_{chebi_id}.dre"
                        with open(mol_filename, "w") as mf:
                            mf.writelines(mol_lines)
                        atoms, bonds = parse_mol_lines(mol_lines)
                        write_dreadnaut(atoms, bonds, dre_filename)
                        print(f"CHEBI_{chebi_id} généré")
                        found = True
                        break  # on a trouvé la mol

                # Reset pour prochaine molécule
                mol_lines = []

    if mode == "chebi" and not found:
        print(f"CHEBI:{param} non trouvé dans {sdf_file}")

# -------------------------- Main ---------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Parser SDF → fichiers MOL et DRE")
    parser.add_argument("sdf_file", help="Chemin du fichier SDF")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Générer toutes les molécules")
    group.add_argument("--first", type=int, help="Générer les X premières molécules")
    group.add_argument("--chebi", type=int, help="Générer une seule molécule avec son ChEBI_ID")
    args = parser.parse_args()

    if args.all:
        process_sdf(args.sdf_file, "all")
    elif args.first:
        process_sdf(args.sdf_file, "first", args.first)
    elif args.chebi:
        process_sdf(args.sdf_file, "chebi", args.chebi)

if __name__ == "__main__":
    main()
