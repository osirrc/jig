#!/usr/bin/env bash

BASE=`pwd`

# Clone and compile trec_eval
git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval

WGET=wget
if [[ "$OSTYPE" == "darwin"* ]]; then
	WGET="curl -O"
fi

# Download topics
mkdir topics && cd topics
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/topics.core17.txt
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/topics.core18.txt
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/topics.robust04.301-450.601-700.txt

# Back to root dir
cd $BASE

# Download qrels
mkdir qrels && cd qrels
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.core17.txt
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.core18.txt
$WGET https://raw.githubusercontent.com/castorini/Anserini/master/src/main/resources/topics-and-qrels/qrels.robust2004.txt

