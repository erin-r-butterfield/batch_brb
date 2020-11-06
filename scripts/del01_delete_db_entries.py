#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

import argparse, sqlite3, sys

#Defining arguments
parser = argparse.ArgumentParser(description='Delete BLAST database details from SQLite3 database')

parser.add_argument('-db',help='SQLite3 database')

parser.add_argument('-name',help='Name of BLAST database')

parser.add_argument('-alias', action='store_true', help='BLAST database is an alias database, default= FALSE')

parser.add_argument('-type' ,help='Data type either nucl or prot')



args = parser.parse_args()


#Defining variables
name = str(args.name)
db = str(args.db)
alias = args.alias
data = args.type
if data == 'prot':
    table_name = 'data_prot'
else:
    table_name = 'data_nucl'



#Connecting to SQLite3 database
conn = sqlite3.connect(db)
c = conn.cursor()


#Deleting data from SQLite3 database
if alias:
    c.execute('''DELETE FROM alias_databases WHERE aliasdb = (?);''', (name,))
    conn.commit()

else:
    c.execute('''DELETE FROM user_data WHERE blastdb = (?);''', (name,))
    c.execute('''DELETE FROM %s WHERE document = (?);''' % table_name, (name,))
    conn.commit()
