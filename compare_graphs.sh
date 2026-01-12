#!/bin/bash
# Script pour tester l'isomorphisme entre deux fichiers .dre

# Vérifie que deux fichiers .dre sont passés en argument
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 molecule1.dre molecule2.dre"
    exit 1
fi

MOL1="$1"
MOL2="$2"

# Extraire les noms sans extension
BASE1="${MOL1%.*}"
BASE2="${MOL2%.*}"

#  Convertir en graph6
echo "Conversion en graph6..."
./dretog -g "$MOL1" "${BASE1}.g6"
./dretog -g "$MOL2" "${BASE2}.g6"

# Canoniser avec labelg
echo "Canonisation..."
./labelg "${BASE1}.g6" > "${BASE1}_canon.g6"
./labelg "${BASE2}.g6" > "${BASE2}_canon.g6"

#  Comparer les graphes canonisés
echo "Comparaison..."
if diff "${BASE1}_canon.g6" "${BASE2}_canon.g6" > /dev/null ; then
    echo " Les molécules sont isomorphes !"
else
    echo " Les molécules NE SONT PAS isomorphes."
fi
