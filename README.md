#OptiVac - Designing String-of-beads with optimal spacers

Authors: Benjamin Schubert and Oliver Kohlbacher
Date: June 2015
Version: 1.0
License: This software is under a three-clause BSD license


Introduction:
-------------
The software is a novel approach to construct epitope-based string-of-beads
vaccines in optimal order and with sequence-optimized spacers of flexible length
such that the recovery of contained epitopes is maximized and immunogenicity of 
arising neo-epitopes is reduced. 

Requirement:
-------------
Spacer Design uses the following software and libraries:
1) Python 2.7 (https://www.python.org/)
2) Fred2 (https://github.com/FRED-2/Fred2)
3) Cplex >= 12.5 (www.ilog.com)
4) LKH TSP-Approximation >= 2.0.7 (http://www.akira.ruc.dk/~keld/research/LKH/)

Please make sure you have installed said software/libraries
and their dependencies.


Installation:
-------------
First install all required software and libraries. CPLEX/LKH should be globally executable
via command line. 


Usage:
-------------
usage: spacer_design.py [-h] -i INPUT -a ALLELES [-k MAX_LENGTH] [-al ALPHA]
                        [-be BETA] [-thr THRESHOLD] -o OUTPUT [-t THREADS]

The software is a novel approach to construct epitope-based string-of-beads
vaccines in optimal order and with sequence-optimized spacers of flexible
length such that the recovery of contained epitopes is maximized and
immunogenicity of arising neo-epitopes is reduced.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        File containing epitopes (one peptide per line)
  -a ALLELES, --alleles ALLELES
                        Specifies file containing HLA alleles with
                        corresponding HLA probabilities (one HLA per line)
  -k MAX_LENGTH, --max_length MAX_LENGTH
                        Specifies the max. length of the spacers (default 6)
  -al ALPHA, --alpha ALPHA
                        Specifies the first-order preference of the user in
                        the model [0,1] (default 0.99)
  -be BETA, --beta BETA
                        Specifies the second-order preference of the user in
                        the model [0,1] (default 0).
  -thr THRESHOLD, --threshold THRESHOLD
                        Specifies epitope prediction threshold for SYFPEITHI
                        (default 20).
  -o OUTPUT, --output OUTPUT
                        Specifies the output file.
  -t THREADS, --threads THREADS
                        Specifies number of threads. If not specified all
                        available logical cpus are used.
