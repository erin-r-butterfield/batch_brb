#!/usr/bin/env bash

# This software was created by the Wellcome Centre for Anti-Infectives Research using Wellcome Trust funding
# batch_brb  Copyright (C) 2020  University of Dundee
# For full details see LICENSE.txt or http://www.gnu.org/licenses/

#Get command line arguments
while :; do
    case $1 in
    	-h|--help)
      	echo " "
      	echo "This script will create a BLAST database from a fasta file and add the accessions to a SQLite3 database."
      	echo " "
      	echo "USAGE: mdb01_makeblastdb.sh -in [options]"
      	echo " "
      	echo "options:"
      	echo "-h, --help 			show brief help"
      	echo "-in, --infile       	        REQUIRED; fasta file to create BLAST database from"
        echo "-db, --database      		OPTIONAL; Name of SQLite3 database, default is accession_db.db "
      	exit 0
      	;;
        -in|--infile) INFILE="$2" 
        shift        
        ;;
        -db|--database) DB=$2
        shift          
        ;;
        *) break
    esac
    shift
done

pattern=' '
# SCRIPT_PATH="$CONDA_PREFIX/bin"

#Error if no input file
if [ -z "$INFILE" ]
then
    echo "Error: Input file required"
    exit 1
fi


#If db not supplied then set database to default
if [ -z "$DB" ]
then
    DB=accession_db.db
fi

#Check no illegal characters in fields
if [[ "$INFILE" =~ ^[0-9] ]] || [[ "$DB" =~ ^[0-9] ]];
then
    echo 'Error: Infile and database cannot start with a number'
    exit 1
fi


if [[ "$DB" =~ $pattern ]]
then
    echo 'Error: database and name cannot contain spaces'
    exit 1
fi

if [[ "$INFILE" =~ $pattern ]]
then
    mv "$INFILE" "${INFILE// /_}"
    INFILE="${INFILE// /_}"
fi


#Get file name
BASE="${INFILE##*/}"
FBNAME="${BASE%.*}"
NAME="$FBNAME"

#Make BLAST database pipeline
echo "#### $INFILE ####"

#Test file is valid fasta format and whether it is protein or nucleotide
seqkit stats "$INFILE" -T > "${FBNAME}"_stats_output.txt

echo "Detecting file type:"
if tail -n +2 "${FBNAME}"_stats_output.txt | cut -f2 | grep "FASTA"
echo "Detecting data type:"
then 
    if tail -n +2 "${FBNAME}"_stats_output.txt | cut -f3 | grep "Protein"
    then
        DBTYPE='prot'
        echo "DBTYPE: $DBTYPE"
        rm "${FBNAME}"_stats_output.txt
    else
        DBTYPE='nucl'
        echo "DBTYPE: $DBTYPE"
        rm "${FBNAME}"_stats_output.txt
    fi


    echo
    #Add accessions to the SQLite3 database
    while :
    do
        set -o noclobber
        if { > lock_file ; } &> /dev/null
        then
            python mdb02_convert_headers.py "$INFILE" "${FBNAME}"_converted.fasta -db "$DB" -blastdb "$FBNAME"
            SUCCESS=$?
            set +o noclobber
            rm lock_file
            break
        fi
        echo "lock file detected, sleeping...."
        date +"%H:%M:%S"
        sleep 2
    done

    if [ "$SUCCESS" -ne "0" ] ; then
        rm "${FBNAME}"_converted.fasta
        echo
        echo
        exit 1
    fi


    INFILE2="${FBNAME}"_converted.fasta
    ORIGINAL="$FBNAME"
    BASE="${INFILE2##*/}"
    FBNAME="${BASE%.*}"


    #Add accessions to the SQLite3 database
    while :
    do
        set -o noclobber
        if { > lock_file ; } &> /dev/null
        then
            python mdb03_add_to_db.py -infile "${FBNAME}".fasta -name "$ORIGINAL" -db "$DB" -type "$DBTYPE"
            SUCCESS=$?
            set +o noclobber
            rm lock_file
            break
        fi
        echo "lock file detected, sleeping...."
        date +"%H:%M:%S"
        sleep 2
    done
    
    if [ "$SUCCESS" -eq "0" ] ; then
        echo "Accessions added to SQLite3 database: $DB"
        #Create BLAST database from input fasta file
        makeblastdb -in "$INFILE2" -dbtype "$DBTYPE" -parse_seqids -out "${ORIGINAL}_database"
        BLAST_SUCCESS=$?
        if [ "$BLAST_SUCCESS" -ne 0 ]
        then
            while :
            do
                set -o noclobber
                if { > lock_file ; } &> /dev/null
                then
                    python del01_delete_db_entries.py -db "$DB" -name "$ORIGINAL" -type "$DBTYPE"
                    echo "Accessions removed from SQLite3 database: $DB"
                    set +o noclobber
                    rm lock_file
                    rm "$INFILE2"
                    break
                fi
                echo "lock file detected, sleeping...."
                date +"%H:%M:%S"
                sleep 2
            done
        fi
    else
        echo "Error: Accessions or name already present in the database"
        rm "$INFILE2"
        echo
        echo
        exit 1
    fi
    
else 
    echo "Error: Input file $INFILE invalid FASTA format"
    rm "${FBNAME}"_stats_output.txt
    exit 1
fi


