Shakespeare Search Engine
=========================

Author: Shuo Yang
Email: imsure95@gmail.com

Introduction
=========================

A small Shakespeare search engine.
It is my course project for SEIS731 "Information Retrieval" at University of St. Thomas.

It can let you perform both free text query and phrase query
against Shakespeare's whole collection (except Poetry) based on a command line interface.

The system contains a crawler, indexer and a query processor.

The crawler crawls Shakespeare's whole collection from http://shakespeare.mit.edu/.

The indexer then builds inverted index based on the whole collection that have been crawled.


How to use
=========================

To crawl data and build index, run:
$ cd src
$ chmod +x run_crawler_indexer.sh

After this, to start query, run:
$ python query.py

Query demos
=========================
Free text query (Four terms chosen from Hamlet Act2, Scene 2A):
Enter a query:(If you want to quit, type 'q')
quintessence apprehension angel paragon

RANK                                           DOCUMENT(SCORE)                                           
-----------------------------------------------------------------------------------------------------
1    ./whole_collection/Tragedy/Hamlet/Act_2_Scene_2A_room_in_the_castle.txt (1.00)
2    ./whole_collection/Comedy/As_You_Like_It/Act_3_Scene_2The_forest.txt (0.70)
3    ./whole_collection/Comedy/The_Tempest/Act_2_Scene_1Another_part_of_the_island.txt (0.57)

Phrase query (the phrase chosen from Hamlet Act 3 Scene 1A):
Enter a query:(If you want to quit, type 'q')
'to be or not to be, that is the question'

Matching documents:
./whole_collection/Tragedy/Hamlet/Act_3_Scene_1A_room_in_the_castle.txt


Report
=========================
For the detailed report of this project, please see:
https://github.com/imsure/Shakespeare_Search_Engine/blob/master/project_report_Shuo_Yang.pdf