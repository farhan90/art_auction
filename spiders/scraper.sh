#!/bin/bash

while read line;do
	scrapy crawl exp_art -a s_url=$line -o $2	
done < $1
