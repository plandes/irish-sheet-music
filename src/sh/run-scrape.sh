#!/bin/sh

NUM=$1
ABC=../../data/abc/
SS=./perl/scrapesession

if [ -z "$NUM" ] ; then
    echo "usage: $0 <session id>"
    exit 1
fi

echo "add this to tunes-list.numbers:"
${SS} $NUM
${SS} -f abc $NUM > ${ABC}/$NUM.abc
