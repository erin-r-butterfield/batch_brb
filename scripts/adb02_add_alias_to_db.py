#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/


import argparse, sqlite3, sys

#Defining arguments
parser = argparse.ArgumentParser(description='Add alias database information to SQLite3 database')

parser.add_argument('-infile',help='List of accessions')

parser.add_argument('-db',help='SQLite3 database')

parser.add_argument('-name',help='Name of alias database')

args = parser.parse_args()


#Defining variables
infile = args.infile
name = str(args.name)
db = str(args.db)



#Connecting to SQLite3 database
conn = sqlite3.connect(db)
c = conn.cursor()



#Creating a data table if non exists
c.execute('''CREATE TABLE IF NOT EXISTS alias_databases (
    id INTEGER PRIMARY KEY,
    aliasdb TEXT,
    blastdb TEXT);''')
conn.commit()



with open(infile, "r") as f:
    dbs = [(name, line.rstrip('\n')) for line in f]


# print(dbs)

#Check if aliasdb name already present in database
c.execute('''SELECT * FROM alias_databases WHERE aliasdb = (?) LIMIT 1;''', (name,))
row = c.fetchone()
# print(row)


#If aliasdb name present in database exit script else add aliasdb information to database
if row:
    print("Alias database name already in " + db + ", please choose another name")
    sys.exit(1)
else:
    c.executemany('''INSERT INTO alias_databases (aliasdb, blastdb) VALUES (?,?);''', dbs)
    conn.commit()
    