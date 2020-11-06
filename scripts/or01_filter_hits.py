#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, sqlite3
import pandas as pd
import batch_brb_functions as bbrbf


parser = argparse.ArgumentParser(description='This script filters first BLAST results to extract results which are within the top x number of hits for an organism and have an alignment length >= user set percentage of query.')

parser.add_argument('fblast_file',help='First BLAST results file with columns: qseqid, sseqid, pident, length, mismatch, gapopen, qstart, qend, sstart, send, evalue, bitscore, gaps, qcovs, qcovhsp, qlen, slen')

parser.add_argument('outfile',help='Name of output')

parser.add_argument('hit_num',type=int,help='Integer, Number of hits to include')

parser.add_argument('coverage',type=int,help='Integer, Coverage of alignment (percentage)')

parser.add_argument('database',help='Name of SQLite3 database')

parser.add_argument('type',help='Type of data; nucl or prot')

args = parser.parse_args()

# Define variables
fblast_file = args.fblast_file
output = args.outfile
hit_num = args.hit_num
coverage = args.coverage
db = args.database
data = args.type

conn = sqlite3.connect(db)
c = conn.cursor()




#Read in data and add organism information
fbfile = bbrbf.import_blast_results(fblast_file)

df1 = bbrbf.merge_orgs(fbfile, c, data)
# print(df1.head())
# print(dfx.shape)

df1.to_csv(path_or_buf= (output + "_FB.txt"), sep= "\t", index= False, columns= ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen", "document"])



#Filter results
df2 = bbrbf.FB_get_top_hits(df1,hit_num)
# print(df1)

df3 = bbrbf.coverage_check(df2,coverage)
#print(df2)

df4 = df3.loc[df3["coverage"] == True]
#print(df3)

final_accessions = df4.sseqid.unique().tolist()
#print(final_accessions)



#Export data
f = open(output + "_hits.txt", 'w')
for item in final_accessions:
  f.write("%s\n" % item)
f.close()

df4.to_csv(path_or_buf= (output + "_filtered_FB.txt"), sep= "\t", index= False, columns= ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen", "document"])





