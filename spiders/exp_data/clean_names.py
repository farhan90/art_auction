#!/usr/bin/python

import re


f= open('artists.txt','r+')

for line in f.readlines():
	mObj=re.search(r'([^\/][a-z-]*_)',line)
	if mObj!=None:
		temp_name=mObj.group(0)
		matchObj=re.match('(.*[^_])',temp_name)
		name=matchObj.group(1)
		name=name.replace('-',' ')
		name=name.title()
		print name

