#!/usr/bin/env bash

# Clone and compile trec_eval
git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval

# Download qrels
mkdir qrels && cd qrels
wget https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.core17.txt
wget https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.core18.txt
wget https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.robust2004.txt