#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, os, sqlite3
import pandas as pd
import numpy as np
import batch_brb_functions as bbrbf

parser = argparse.ArgumentParser(description='This script filters reverse BLAST results to extract results which are within the top x number of hits for an organism and have an alignment length >= user set percentage of query.')

parser.add_argument('rblast_file',help='Input BLAST file with the following columns: qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore gaps')

parser.add_argument('fblast_file',help='Filtered First BLAST file with the following columns: qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore gaps document')

parser.add_argument('outfile',help='Name of output')

parser.add_argument('hit_num',type=int,help='Integer, Number of hits to include')

parser.add_argument('coverage',type=int,help='Integer, Coverage of alignment (percentage)')

parser.add_argument('-sqldb',help='name of SQLite3 database')

parser.add_argument('-blastdb',help='name of first BLAST database if alias database was used')

args = parser.parse_args()

# Define variables
rblast_file = args.rblast_file
fblast_file = args.fblast_file
output = args.outfile
hit_num = args.hit_num
coverage = args.coverage
db = args.sqldb
blastdb = args.blastdb


#Connecting to SQLite3 database
if db:
    conn = sqlite3.connect(db)
    c = conn.cursor()


#Import file and get hits
rbfile = bbrbf.import_blast_results(rblast_file)
rbfile.to_csv(path_or_buf= (output + "_RB.txt"), sep= "\t", index= False, columns= ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen"])
# print(rbfile.dtypes)

df = bbrbf.RB_get_top_hits(rbfile, hit_num)
#print(df.head())

df2 = bbrbf.coverage_check(df,coverage)
#print(df2.head())

df3 = df2.loc[df2["coverage"] == True]
#print(df3)

df4 = bbrbf.import_filtered_results(fblast_file)
#print(df4.head())

df5 = pd.merge(df3, df4, how= "inner", left_on=["qseqid", "sseqid"], right_on=["sseqid", "qseqid"])
# print(df5)
# df5.to_csv(path_or_buf= (output + "_orthologs_list.txt"), sep="\t")

orthologs = df5[["qseqid_y", "sseqid_y", "document_y"]]
orthologs2 = orthologs.drop_duplicates()
# print(orthologs)


df6 = orthologs2.pivot_table(index= ["qseqid_y", "document_y"], values= "sseqid_y", aggfunc= lambda x: ", ".join(x))
df6 = df6.rename_axis(index= {"qseqid_y":"Accession"})
#print(df6)


## Convert dataframe to wide format
stacked = df6.unstack(fill_value= "NA")
stacked.reset_index()
stacked.columns = stacked.columns.get_level_values(1)
# print(stacked)


## Add null organisms if from alias database
if db:
    ## Get database organisms and results organisms
    c.execute('''SELECT blastdb FROM alias_databases WHERE aliasdb = (?);''', (blastdb,))
    db_orgs = [item[0][:-len('_database')] for item in c.fetchall()]
    # print(db_orgs)
    res_orgs = list(stacked.columns)
    # print(res_orgs)


    ## Add organisms from database for which no orthologs were obtained and order alphabetically
    diff = np.setdiff1d(db_orgs, res_orgs)
    diff = diff[diff != '']
    # print(diff)
    for org in diff:
        stacked[org] = 'NA'
    # print(stacked)
    stacked = stacked.reindex(sorted(stacked.columns), axis=1)


#Write to file
stacked.to_csv(path_or_buf= (output + "_orthologs.csv"))
