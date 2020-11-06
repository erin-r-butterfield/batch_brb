#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, sqlite3, hashlib
from Bio import SeqIO
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description='Retrieve accessions corresponding to input fasta file from SQLite3 database and where not found create a fasta file which can be used for BLAST')

parser.add_argument('-fa',help='Fasta file of accessions to retrieve')

parser.add_argument('-out',help='Name of output')

parser.add_argument('-db',help='SQLite3 database')

parser.add_argument('-name',help='Name of BLAST database')

parser.add_argument('-type',help='Data type either nucl or prot')

args = parser.parse_args()


#Assign variables
infile = args.fa
output = args.out
name = str(args.name)
db = str(args.db)
data = str(args.type)
if data == 'prot':
    table_name = 'data_prot'
else:
    table_name = 'data_nucl'

l1 = []
l2 = []
l3 = []
d1 = {}


#Connecting to SQLite3 database
conn = sqlite3.connect(db)
c = conn.cursor()


#Extracting accessions, creating md5 hashes for sequences, building lists for SQL queries
handle = open(infile, "r")
for record in SeqIO.parse(handle, "fasta"):
        header = record.id
        seq = record.seq
        encode = hashlib.md5(seq.encode())
        l1.append('(?)')
        l2.append((header, encode.hexdigest()))
        l3.append(encode.hexdigest())
        d1[header] = str(seq)
            
# print(l2)
# print(l3)


#Retrieve md5 hashes from SQLite3 database and filter to only contain the organism looking for
c.execute('''SELECT accession, document, md5 FROM %s WHERE md5 IN (''' % table_name + ','.join(l1) +''');''',l3)
df = pd.DataFrame(c.fetchall(), columns= ['database_accession', 'document', 'md5'])
filtered = df.loc[(df['document'] == name)]
# print(filtered.head()) 


#Build a dataframe of the input sequences, merge with the database results and output 
inputs = pd.DataFrame(l2, columns= ['input_accession', 'md5'])
merged = inputs.merge(filtered, how='left', on='md5')
merged2 = merged.replace(np.nan, 'Not identified', regex=True)
# print(merged2)
merged2.to_csv(path_or_buf=(output + "_db_accessions.csv"), columns= ['input_accession', 'database_accession'], index= False)


#Extract accessions not found and output fasta file of these sequences
not_id_df = merged2.loc[(merged2['database_accession'] == 'Not identified')]
# print(not_id_df)
not_id_ls = not_id_df.input_accession.unique()

if len(not_id_ls) > 0:
    with open((output + "_missing.fasta"), 'w') as out_handle:
        for i in not_id_ls:
            out_handle.write('>' + i + '\n' + d1[i] + '\n')
    print('Not all sequences in database please see BLAST results for missing accessions')
