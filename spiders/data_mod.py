#!/usr/bin/env python

import numpy

import pandas as pd


df=pd.read_csv("data.csv")
df=df[~df['actual_price'].str.contains('actual_price')]

df=df[['name','title','currency','lower_estimate','upper_estimate','actual_price']]

df.to_csv('art_data.csv')
