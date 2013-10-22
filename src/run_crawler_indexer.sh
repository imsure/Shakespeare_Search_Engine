#!/bin/bash

START=$(date +%s)
python crawler.py http://shakespeare.mit.edu
python indexer.py
END=$(date +%s)
TIME_DIFF=$(( $END - $START ))
echo
echo "It took" $TIME_DIFF "seconds to run crawler and indexer."
echo