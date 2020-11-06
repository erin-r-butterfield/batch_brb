#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, random, string, sqlite3, re, sys
from Bio import SeqIO
import pandas as pd
import batch_brb_functions as bbrbf

parser = argparse.ArgumentParser(description='Convert fasta file headers to a format compatible with BLAST and orthology pipeline, adds a unique identifier to accessions and adds unique identifier to SQLite3 database')

parser.add_argument('infile',help='Fasta file')

parser.add_argument('outfile',help='Name of output')

parser.add_argument('-db',help='SQLite3 database')

parser.add_argument('-blastdb', help='Name of BLAST database to be created later in pipeline')



args = parser.parse_args()

# Define variables
infile = args.infile
output = args.outfile
db = str(args.db)
blastdb = str(args.blastdb)


#Connecting to SQLite3 database
conn = sqlite3.connect(db)
c = conn.cursor()

#Creating a data table if non exists
c.execute('''CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY,
    unique_id TEXT,
    file TEXT,
    blastdb TEXT)''')
conn.commit()


#Check infile and blastdb not already present in BLAST database
c.execute('''SELECT file, blastdb FROM user_data WHERE file = (?) OR blastdb = (?);''', (infile, blastdb))
rows = [(item[0], item[1]) for item in c.fetchall()]
if rows:
    print('Error: the following file or BLAST database already present in ' + db )
    [print('file: ' + item[0] + ', BLAST database: ' + item[1]) for item in rows]
    print('Please either change names, add more information (e.g. strain) or remove previous entries by deleting the BLAST database using deleted_database.sh')
    sys.exit(1)


identifier = bbrbf.get_id(4, conn, infile, blastdb) + '_'


#Convert the headers of the fasta file
with open(infile, "r") as handle, open((output), 'w') as corrected:
    for record in SeqIO.parse(handle, "fasta"):
        header = record.id
        split = header.split('|')
        # print(split[0])
        if split[0] == "jgi":
            # print("Data source: JGI")
            new_header =  identifier + split[2] + " " + split[1]
        elif split[0] == "ENA":
            # print("Data source: ENA")
            new_header = identifier + split[1]
        else:
            split = header.split(' ')
            # print(split)
            if re.match('^..\|', split[0]) or re.match('^...\|', split[0]):
                # print('success')
                split2 = split[0].split('|')
                new_header = identifier + split2[1]
            elif len(split[0]) >= 44:
                split2 = split[0].split('|')
                new_header = identifier + split2[0]
            else:
                # print('no')
                new_header = identifier + split[0]
        record.id = new_header
        SeqIO.write(record, corrected, 'fasta')
