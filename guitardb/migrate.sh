#!/bin/bash
export INPUT=/mnt/data/Igrek/guitarDB
export OUTPUT=/mnt/data/Igrek/guitarDB/songs.sqlite

./guitardb_migrate.py --input $INPUT --output $OUTPUT
