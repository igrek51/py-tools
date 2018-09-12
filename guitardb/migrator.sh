#!/bin/bash
export INPUT=/mnt/data/Igrek/guitarDB
export OUTPUT=/mnt/data/Igrek/guitarDB/songs.sqlite
export DB_VERSION_NUMBER=5

./guitardb_migrate.py --input $INPUT --output $OUTPUT --versionNumber $DB_VERSION_NUMBER
