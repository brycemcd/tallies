#!/bin/bash

## Silly script to create tallies of things
## Usage:
## ./create_tally beer
## That would log one beer with the timestamp of when the server received and processed the request


if [ -z ${1+x} ]; then
    echo "The first argument should be set to the thing you want to tally i.e. ./create_tally beer to tally one beer"
    exit 1

else echo "Tallying one '$1'";
TALLYABLE=$1

fi

HOST=10.1.2.228
PORT=5000
# NOTE: at some point, I'll create a DNS entry for this app so it can move safely
echo $(curl -XPOST -# http://${HOST}:${PORT}/v1/tally/${TALLYABLE})

