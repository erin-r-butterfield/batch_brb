#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import os, argparse
import pandas as pd
import batch_brb_functions as bbrbf



parser = argparse.ArgumentParser(description='This script will convert a csv of ortholog results into text files compatible with the FastTree pipeline')

parser.add_argument('csv',help='CSV of ortholog results, first column must be queries with header Accession, remaining columns should be orthology results with one organism per column')

args = parser.parse_args()

csv_file = args.csv


#Create Trees folder if none exists
try: 
    os.mkdir("Trees")
except OSError:
    pass



#Read in data and convert into long format
df = pd.read_csv(csv_file)
# print(df)

df2 = pd.melt(df, id_vars=['Accession'])
# print(df2)

#Split rows which contain multiple accessions code adapted from:
#https://stackoverflow.com/questions/17116814/pandas-how-do-i-split-text-in-a-column-into-multiple-rows/21032532
s = df2['value'].str.split(', ').apply(pd.Series, 1).stack()
s.index = s.index.droplevel(-1)
s.name = 'value' 
del df2['value']

df3 = df2.join(s)
df4 = df3.dropna()
# print(df3)


#Create a text file for each query containing all ortholog accession results for that query
queries = df4.Accession.unique()
# print(queries)

for item in queries:
	df5 = df4.loc[df4["Accession"] == item]
	l1 = df5.value.unique().tolist()
	no_illegal = bbrbf.replace_illegal(item)
	# print(l1)
	name = r"Trees/A_" + no_illegal + ".txt"
	f = open(os.path.join(os.getcwd(),name), 'w')
	for accession in l1:
  		f.write("%s\n" % accession)
	f.close()