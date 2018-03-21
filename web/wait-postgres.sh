#!/bin/bash

while true; do
COUNT_PG=`psql postgresql://postgres:postgres@localhost:5432/massing -c '\l \q' | grep "massing" | wc -l`
if ! [ "$COUNT_PG" -eq "0" ]; then
    break
fi
    echo "Waiting Database Setup"
    sleep 10
done