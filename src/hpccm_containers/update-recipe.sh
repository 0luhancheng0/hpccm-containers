#!/bin/bash
for i in *; do
    if [ -d "$i" ] && [ -f "$i/$i.py" ]; then
        cd $i && python $i.py > Singularity.$i && cd ..
    fi
done

