#!/bin/bash

# NOTE: tally_root is a 'magic' user (see 01-add_app_user.sql)
# NOTE: tallyable should match whatever the voice command has enumerated
# FIXME: put voice command and db enumerable into a common place
psql -v ON_ERROR_STOP=1 --username "tally_root" --dbname "tallies" <<-EOSQL

    CREATE TABLE tallyable_items(
        id SERIAL PRIMARY KEY
        , tallyable_item TEXT UNIQUE NOT NULL
        , insert_dttm TIMESTAMP NOT NULL DEFAULT NOW()
    );

    INSERT INTO tallyable_items (tallyable_item) VALUES
    ('beer'),
    ('wine'),
    ('whiskey');


    CREATE TABLE tallies(
        id SERIAL PRIMARY KEY
        , tally_dttm TIMESTAMP NOT NULL DEFAULT NOW()
        , tallyable_item INT NOT NULL REFERENCES tallyable_items(id)
    )
EOSQL