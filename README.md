# batch_brb
## Introduction
batch_brb is a command-line application for automated best reciprocal BLAST.  Common ortholog identification methods can have organism availability limitations and difficulty identifying divergent sequences.  These issues can be overcome with manual searching but this is a time consuming and tedious process making it unsuitable for moderate to larger scale analyses.  batch_brb provides tools to automate the data collection process while maintaining flexibility in hit selection criteria, enabling the analysis of greater numbers of sequences.  

batch_brb performs ortholog identification using best reciprocal BLAST.  Sequences of interest are searched against a user created database.  The top x hits per query per organism are extracted and filtered by y coverage of the query where x and y are specified by the user.  Identical hits do not contribute to the hit count.  These hits are searched against the organism of the original query sequences.  The top x hits per query are  filtered by y query coverage as above.  Where the hits from the first and reverse BLAST match, the sequences are considered orthologs.  batch_brb is designed to enable maximum coverage and requires user analysis of hits for the exclusion of mishits and paralogs. 

## Documentation
See the batch_brb_manual in the documentation folder for usage instructions

## Quick start
batch_brb is available as a Bioconda package and requires [Conda](https://docs.conda.io/en/latest/miniconda.html) and [Bioconda](https://bioconda.github.io/user/install.html).  On Linux/Unix-like operating system:
```
conda create -n batch_brb batch_brb
conda activate batch_brb
```
Change into the directory where batch_brb should be located and run:
```
batch_brb_setup
```

## Contact info
For general enquiries please contact ebutterfield@dundee.ac.uk, to report issues 
please use the [GitHub issue tracker](https://github.com/erin-r-butterfield/batch_brb/issues).

## How to cite batch_brb
A protocol publication describing batch_brb is currently in preparation.  In the meantime please cite the [GitHub repository](https://github.com/erin-r-butterfield/batch_brb).  Please also cite the dependency publications, see documentation for a list of dependencies.

## Acknowledgements
This software was created by the Wellcome Centre for Anti-Infectives 
Research using Wellcome Trust funding.

Thank you to Tim Butterfield, Frederik Drost and Michele Tinti for comments on the code 
and to Ricardo Canavate del Pino and Ning Zhang for help with testing.

## Licence
Copyright (C) 2020  University of Dundee

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

