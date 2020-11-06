#!/usr/bin/env python

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

#### This script contains functions used by batch_brb pipelines

import pandas as pd
import random, string

def get_random_alphanumeric_string(length):
    """Gets random alphanumeric string with first character set to either upper or lower case letter
    adapted from: https://pynative.com/python-generate-random-string/#:~:text=If%20you%20want%20to%20generate,string%20constant%20using%20a%20random"""
    letter = random.choice(string.ascii_letters)
    letters_and_digits = string.ascii_letters + string.digits
    result_str = letter + ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def check_id(unique_id, db_connection):
	"""Checks if accessions already present in SQLite3 database"""
	c = db_connection.cursor()
	c.execute('''SELECT * FROM user_data WHERE unique_id = (?);''', (unique_id,))
	row = c.fetchall()

def get_id(length, db_connection, infile, blastdb):
	"""Create a random id to insert at the beginning of the accessions in fasta file"""
	c = db_connection.cursor()
	while True:
		unique = get_random_alphanumeric_string(4)
		# print(unique)
		row = check_id(unique, db_connection)
		# print(row)
		if row == None:
			c.execute('''INSERT INTO user_data (unique_id, file, blastdb) VALUES (?,?,?);''', (unique, infile, blastdb))
			db_connection.commit()
			return unique


def import_blast_results(file):
	"""Return pandas dataframe of input blast file"""
	df = pd.read_csv(file, sep="\t", names = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen"], dtype={"qseqid": "object", "sseqid": "object", "pident": "object", "evalue": "object", "bitscore": "object"})
	return df

def import_filtered_results(file):
	"""Return pandas dataframe of input blast file"""
	df = pd.read_csv(file, sep="\t", header=0, names = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen", "document"], dtype={"qseqid": "object", "sseqid": "object", "pident": "object", "evalue": "object", "bitscore": "object"})
	return df

def get_accessions(dataframe):
	"""Return a list of unique query accessions present in the blast input file"""
	df = dataframe
	names = df.qseqid.unique()
	#print(names)
	return names


def check_duplicate(dataframe):
	"""Return dataframe with two columns added indicating which subjects are duplicates (in terms of result not identifier).  
	The first column includes the first instance of the duplication the second column does not include the first instance of the duplication"""
	df = dataframe
	subset = df.drop("sseqid", axis=1)
	df["duplicate"] = subset.duplicated(keep=False)
	df["dup_non_incl"] = subset.duplicated(keep="last")
	#print(df)
	return df

def single_subject(dataframe):
	"""Returns a dataframe with a column added to indicate whether the row is the first instance of the query (qseqid), subject (sseqid) pairing."""
	df = check_duplicate(dataframe)
	subset = df[["qseqid","sseqid"]]
	df["single"] = subset.duplicated()
	return df


def get_top_hits(dataframe,hits,accession_list):
	"""Returns a dataframe which contains the top hits for the query (qseqid), where the number of hits is specified by the user.
	The number of hits returned is increased to allow for gene duplication as required."""
	df = dataframe
	names = accession_list
	result = pd.DataFrame(columns = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
		"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen", "accession", "document", "duplicate", "dup_non_incl", "single"])
	# result = result_df
	previous = 0
	for i in range(len(names)):
		subset_1 = (df.loc[(df["qseqid"] == names[i]) & (df["single"] == False)].head(hits))
		q_count = (df.loc[(df["qseqid"] == names[i]) & (df["single"] == False)]).shape[0]
		#print("q_count: " + str(q_count))
		#print(subset_1)
		#x = subset_1["duplicate"].sum()
		x = hits
		y = subset_1.loc[(subset_1["dup_non_incl"] == False)].shape[0]
		z = 0
		count = 0
		#print("x start: " + str(x))
		#print("y start: " + str(y))
		while y < hits and q_count > count:
		#	print("hits: " + str(hits))
			x = x + 1
			subset_1 = (df.loc[(df["qseqid"] == names[i]) & (df["single"] == False)].head(x))
		#	print(subset_1)
			y = subset_1.loc[(subset_1["dup_non_incl"] == False)].shape[0]
			count = count + 1
		#	print("x: " + str(x))
		#	print("y: " + str(y))
		#	print("count: " + str(count))
			z = subset_1.shape[0]
		if z == 0:
			result = result.append(df.loc[(df["qseqid"] == names[i]) & (df["single"] == False)].head((hits)))
		else:
			result = result.append(df.loc[(df["qseqid"] == names[i]) & (df["single"] == False)].head(z))
	return result

def FB_get_top_hits(dataframe, hits):
	"""Returns a dataframe which contains the top hits for the query (qseqid) per organism, where the number of hits is specificed by the user.  
	The number of hits returned is increased to allow for gene duplication as required."""
	df = single_subject(dataframe)
	# print(df.head())
	#print(df)
	organisms = df.document.unique()
	# print(organisms)
	accessions = get_accessions(df)
	# print(accessions)
	result = pd.DataFrame(columns = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", 
			"qstart", "qend", "sstart", "send", "evalue", "bitscore", "gaps", "qcovs", "qcovhsp", "qlen", "slen", "duplicate", "dup_non_incl", "single"])
	for i in range(len(organisms)):
		# print(organisms[i])
		subset1 = (df.loc[(df["document"] == organisms[i]) & (df["single"] == False)])
		# print(subset1)
		previous = 0
		#print("previous: " + str(previous))
		result = result.append(get_top_hits(subset1,hits,accessions))
	return result


def RB_get_top_hits(dataframe,hits):
	"""Returns a dataframe which gets the top hits for the query (qseqid), where the number of hits is specified by the user.
	The number of hits returned is increased to allow for gene duplication as required."""
	df = single_subject(dataframe)
	names = get_accessions(dataframe)
	result = get_top_hits(df,hits,names)
	return result


def coverage_check(DataFrame, integer):
	"""Returns a dataframe indicating whether the subject passed the coverage required to be counted, 
	where the coverage is provided by the user"""
	df = DataFrame
	df["coverage"] = df["qcovs"] >= integer
	return df


def get_organisms(dataframe, db_connection, data_type):
	"""Queries an SQLite3 database for the accessions and returns which document they come from, this is returned as a dataframe"""
	l1 = []
	l2 = []
	if data_type == 'prot':
		table_name = 'data_prot'
	else:
		table_name = 'data_nucl'
	accessions = dataframe.sseqid.unique().tolist() 
	for item in accessions:
		l1.append('(?)')
		l2.append(item)
	db_connection.execute('''SELECT accession, document from %s WHERE accession in (''' % table_name + ','.join(l1) + ''');''', l2)
	df = pd.DataFrame(db_connection.fetchall())	
	df.columns = ['accession', 'document']
	df["document"].fillna("Unassigned", inplace=True)
	return df


def merge_orgs(dataframe, db_connection, data_type):
	"""Returns a merged dataframe of BLAST results and organism data obtained from the get_organisms function"""
	org_data = get_organisms(dataframe, db_connection, data_type)
	df = dataframe.merge(org_data, how='left', left_on='sseqid', right_on='accession')
	return df

def replace_illegal(text):
	"""Replaces illegal characters in accession names, adapted from:
	https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string"""
	for ch in ['\\','`','*','{','}','[',']','(',')','>','<','#','+','!','$','\'','|','&','~','\"','?','%',':',';',',','=']:
		if ch in text:
			text = text.replace(ch, '_')
	return text

def melt_df(df):
	"""Convert table to long format"""
	df_long = pd.melt(df, id_vars= ["Accession"])
	df_long.columns = ["Accession", "organism", "hit"]
	return df_long

def split_col_values(df):
	"""Separate mulitvalue cells"""
	df["hit"] = df["hit"].str.split(", ")
	df = (df
	 .set_index(['Accession','organism'])['hit']
	 .apply(pd.Series)
	 .stack()
	 .reset_index()
	 .drop('level_2', axis=1)
	 .rename(columns={0:'hit'}))
	return df