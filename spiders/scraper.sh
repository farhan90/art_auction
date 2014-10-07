#!/bin/bash

for i in $(seq $1 $2);
do
	scrapy crawl art_spider -a num=$i  -o data.csv
done
