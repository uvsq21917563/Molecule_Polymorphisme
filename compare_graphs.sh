#!/bin/bash

#dreadnaut
DREADNAUT="./dreadnaut"

$DREADNAUT < "$1" 2>/dev/null | grep "^[0-9]" > /tmp/mol1.txt
$DREADNAUT < "$2" 2>/dev/null | grep "^[0-9]" > /tmp/mol2.txt

if [ ! -s /tmp/mol1.txt ]; then
    echo "ERREUR: Le fichier dreadnaut n'a rien produit. Vérifiez le script Python."
    exit 1
fi

if diff /tmp/mol1.txt /tmp/mol2.txt >/dev/null; then
    echo "Graphes ISOMORPHES (Structures identiques)"
else
    echo "Graphes DIFFÉRENTS"
fi