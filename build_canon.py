#!/usr/bin/env python3
import os
import subprocess

DRETOG = "../dretog"
LABELG = "../labelg"

dre_files = [f for f in os.listdir(".") if f.endswith(".dre")]
dre_files.sort()

print("Nb graphes :", len(dre_files))

canon_map = {}

for i, dre in enumerate(dre_files):
    g6 = dre.replace(".dre", ".g6")
    canon = dre.replace(".dre", "_canon.g6")

    # dre -> g6
    subprocess.run([DRETOG, "-g", dre, g6], stdout=subprocess.DEVNULL)

    # canonisation
    with open(canon, "w") as out:
        subprocess.run([LABELG, g6], stdout=out)

    # lecture
    with open(canon) as f:
        canon_str = f.read().strip()

    canon_map.setdefault(canon_str, []).append(dre.replace(".dre", ""))

    if i % 1000 == 0:
        print(i, "traités")

# =====================
# Génération pairs.txt
# =====================

from itertools import combinations

pairs = []

for group in canon_map.values():
    if len(group) > 1:
        for a, b in combinations(group, 2):
            pairs.append((a, b))

with open("pairs.txt", "w") as f:
    for a, b in pairs:
        f.write(f"{a} {b}\n")

print("Paires trouvées :", len(pairs))
