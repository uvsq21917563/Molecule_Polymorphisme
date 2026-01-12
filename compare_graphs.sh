#!/bin/bash
# compare_graphs.sh

./dreadnaut < "$1" | grep '\[N' > /tmp/emp1.txt
./dreadnaut < "$2" | grep '\[N' > /tmp/emp2.txt

if diff /tmp/emp1.txt /tmp/emp2.txt >/dev/null; then
    echo "Graphes isomorphes "
else
    echo "Graphes différents "
fi
