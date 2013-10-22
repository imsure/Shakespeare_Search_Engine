Shakespeare Search Engine
=========================

Author: Shuo Yang

Email: imsure95@gmail.com

Introduction
=========================

A small Shakespeare search engine.

It is my course project for SEIS731 "Information Retrieval" at University of St. Thomas, .

It lets you perform both free text query and phrase query against Shakespeare's whole collection (except Poetry) based on a command line interface.

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


Project Report
=========================
For the detailed report of this project, please see:
https://github.com/imsure/Shakespeare_Search_Engine/blob/master/project_report_Shuo_Yang.pdf