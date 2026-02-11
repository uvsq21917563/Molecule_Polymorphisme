#!/bin/bash
set -e

# ================== CONFIG ==================
SDF_GZ="chebi_lite_3_stars.sdf.gz"
SDF_FILE="chebi_lite_3_stars.sdf"
SDF_URL="ftp://ftp.ebi.ac.uk/pub/databases/chebi/SDF/chebi_lite_3_stars.sdf.gz"

PARSER="parser_coloration.py"

DRETOG="./dretog"
LABELG="./labelg"

gcc script.c -o iso -I. nauty.a -lm

# ================== CHECK ARGS ==================
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 CHEBI_ID1 CHEBI_ID2"
    exit 1
fi

ID1="$1"
ID2="$2"

# ================== DOWNLOAD ONCE ==================
if [ ! -f "$SDF_FILE" ]; then
    echo "[+] Téléchargement ChEBI SDF"
    curl -O "$SDF_URL"
    gunzip "$SDF_GZ"
fi

# ================== PARSE MOL → DRE ==================
echo "[+] Génération des .dre"
python3 "$PARSER" "$SDF_FILE" --chebi "$ID1"
python3 "$PARSER" "$SDF_FILE" --chebi "$ID2"

DRE1="CHEBI_${ID1}.dre"
DRE2="CHEBI_${ID2}.dre"

# ================== COMPARAISON ==================
echo "[+] Comparaison des graphes"
./iso "CHEBI_${ID1}.dre" "CHEBI_${ID2}.dre"