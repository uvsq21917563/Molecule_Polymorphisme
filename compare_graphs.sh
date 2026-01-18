#!/bin/bash
set -e

# ================== CONFIG ==================
SDF_GZ="chebi_lite_3_stars.sdf.gz"
SDF_FILE="chebi_lite_3_stars.sdf"
SDF_URL="ftp://ftp.ebi.ac.uk/pub/databases/chebi/SDF/chebi_lite_3_stars.sdf.gz"

PARSER="parser.py"

DRETOG="./dretog"
LABELG="./labelg"

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

# ================== DRE → GRAPH6 ==================
echo "[+] Conversion .dre → graph6"
$DRETOG -g "$DRE1" "CHEBI_${ID1}.g6"
$DRETOG -g "$DRE2" "CHEBI_${ID2}.g6"

# ================== CANONISATION ==================
echo "[+] Canonisation"
$LABELG "CHEBI_${ID1}.g6" > "CHEBI_${ID1}_canon.g6"
$LABELG "CHEBI_${ID2}.g6" > "CHEBI_${ID2}_canon.g6"

# ================== COMPARAISON ==================
echo "[+] Comparaison des graphes"
if diff "CHEBI_${ID1}_canon.g6" "CHEBI_${ID2}_canon.g6" > /dev/null ; then
    echo "Les molécules CHEBI:$ID1 et CHEBI:$ID2 sont ISOMORPHES"
else
    echo "Les molécules CHEBI:$ID1 et CHEBI:$ID2 NE SONT PAS isomorphes"
fi
