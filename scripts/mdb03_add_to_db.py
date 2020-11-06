#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, sqlite3, sys, hashlib
from Bio import SeqIO
from collections import Counter

#Defining arguments
parser = argparse.ArgumentParser(description='This script will add filename and accessions from a fasta file to a SQLite3 database')

parser.add_argument('-infile',help='Input fasta file')

parser.add_argument('-db',help='SQLite3 database')

parser.add_argument('-name',help='Name of fasta file')

parser.add_argument('-type',help='Data type either nucl or prot')

args = parser.parse_args()


#Defining variables
infile = args.infile
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


#Connecting to SQLite3 database
conn = sqlite3.connect(db)
c = conn.cursor()



#Creating a data table if non exists
c.execute('''CREATE TABLE IF NOT EXISTS %s (
    id INTEGER PRIMARY KEY,
    accession TEXT,
    document TEXT,
    md5 TEXT)''' % table_name)
conn.commit()


#Check name not already in database
c.execute('''SELECT * FROM %s WHERE document = (?);''' % table_name, (name,))
row = c.fetchone()
if row:
    print("Error: Name already present in database, please change or add more information e.g. strain")
    sys.exit(1)

   


with open(infile, "r") as handle:
    for record in SeqIO.parse(handle, "fasta"):
            header = record.id
            sequence = record.seq
            encode = hashlib.md5(sequence.encode())
            l1.append('(?)')
            l2.append(header)
            l3.append((header, name, encode.hexdigest()))



#Check if accessions are unique
if len(l2) > len(set(l2)):
    diff = len(l2) - len(set(l2))
    duplicates = Counter(l2).most_common(diff)
    print('Accessions are duplicated in input fasta file, please correct the following accessions:')
    [print(item[0]) for item in duplicates if item[1] > 1]
    c.execute('''DELETE FROM user_data WHERE blastdb = (?);''', (name,))
    conn.commit()
    sys.exit(1)


#Check if accessions already present in database
c.execute('''SELECT * FROM %s WHERE accession IN (''' % table_name + ','.join(l1) +''');''', l2)
row = c.fetchall()


#If one or more accessions present in database exit script else add all accessions to database
if row:
    print("Accessions already present in database")
    print(row)
    sys.exit(1)
else:
    c.executemany('''INSERT INTO %s (accession, document, md5) VALUES (?,?,?);''' % table_name, l3)
    conn.commit()

