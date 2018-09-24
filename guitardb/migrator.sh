#!/bin/bash
export INPUT=/mnt/data/Igrek/guitarDB
export OUTPUT=/mnt/data/Igrek/guitarDB/songs.sqlite
export SONGBOOK_DB=/mnt/data/Igrek/android/songbook/app/src/main/res/raw/songs.sqlite
export DB_VERSION_NUMBER=9

./guitardb_migrate.py --input $INPUT --output $OUTPUT --versionNumber $DB_VERSION_NUMBER

cp ${OUTPUT} ${SONGBOOK_DB}
