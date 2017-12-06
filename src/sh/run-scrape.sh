#!/bin/sh

NUM=$1

if [ -z "$NUM" ] ; then
    echo "usage: $0 <session id>"
    exit 1
fi

echo "add this to tunes-list.numbers:"
#./scrapesession -s $NUM $NUM
./scrapesession $NUM

#./scrapesession -s $NUM -f abc $NUM > ../abc/$NUM.abc
./scrapesession -f abc $NUM > ../abc/$NUM.abc
