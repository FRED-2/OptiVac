#!/usr/bin/env python
# coding=utf-8
"""
###################################################################

Designing String-of-beads with optimal spacers

###################################################################

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
usage: OptiVac.py [-h] -i INPUT -a ALLELES [-k MAX_LENGTH] [-al ALPHA]
                   [-be BETA] [-cp CLEAVAGE_PREDICTION]
                   [-ep EPITOPE_PREDICTION] [-thr THRESHOLD] -o OUTPUT
                   [-t THREADS]

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
  -cp CLEAVAGE_PREDICTION, --cleavage_prediction CLEAVAGE_PREDICTION
                        Specifies the used cleavage prediction method (default
                        PCM) [available: PCM, ProteaSMMConsecutive, ProteaSMMImmuno]
  -ep EPITOPE_PREDICTION, --epitope_prediction EPITOPE_PREDICTION
                        Specifies the used epitope prediction method (default
                        Syfpeithi) [available: Syfpeithi, BIMAS, SMM, SMMPMBEC]
  -thr THRESHOLD, --threshold THRESHOLD
                        Specifies epitope prediction threshold for SYFPEITHI
                        (default 20).
  -o OUTPUT, --output OUTPUT
                        Specifies the output file.
  -t THREADS, --threads THREADS
                        Specifies number of threads. If not specified all
                        available logical cpus are used.
"""

import argparse
import sys
import math
import multiprocessing as mp

from Fred2.IO import FileReader
from Fred2.Core import Allele
from Fred2.Core import Peptide
from Fred2.EpitopePrediction import EpitopePredictorFactory
from Fred2.EpitopeAssembly.EpitopeAssembly import EpitopeAssemblyWithSpacer
from Fred2.CleavagePrediction import CleavageSitePredictorFactory


def generate_alleles(allele_file, generated=None):
    """
                generate allele objects from input
    """
    result=[]
    with open(allele_file, "r") as f:
        for l in f:
            al,freq = l.replace(","," ").replace(";"," ").replace("\n","").split()
            if al.split("HLA-")[-1][0] in ["A","B","C"]:
                result.append(Allele(al,prob=float(freq)))
    return result


def main():
    parser = argparse.ArgumentParser(description="""The software is a novel approach to construct epitope-based string-of-beads
vaccines in optimal order and with sequence-optimized spacers of flexible length
such that the recovery of contained epitopes is maximized and immunogenicity of 
arising neo-epitopes is reduced. """)
    parser.add_argument("-i", "--input",
                        required=True,
                        help="File containing epitopes (one peptide per line)"
    )
    parser.add_argument("-a", "--alleles",
                        required=True,
                        help="Specifies file containing HLA alleles with corresponding HLA probabilities (one HLA per line)"
    )

    #parameters of the model
    parser.add_argument("-k","--max_length",
                        default=6,
                        type=int,
                        help="Specifies the max. length of the spacers (default 6)")
    parser.add_argument("-al","--alpha",
                        default=0.99,
                        type=float,
                        help="Specifies the first-order preference of the user in the model [0,1] (default 0.99)")
    parser.add_argument("-be","--beta",
                        default=0.0,
                        type=float,
                        help="Specifies the second-order preference of the user in the model [0,1] (default 0).")

    parser.add_argument("-cp","--cleavage_prediction",
                        default="PCM",
                        help="Specifies the used cleavage prediction method (default PCM) [available: PCM, PROTEASMM_C, PROTEASMM_S]"
    )
    parser.add_argument("-ep","--epitope_prediction",
                        default="Syfpeithi",
                        help="Specifies the used epitope prediction method (default Syfpeithi) [available: Syfpeithi, BIMAS, SMM, SMMPMBEC]"
    )
    parser.add_argument("-thr","--threshold",
                        default=20,
                        type=float,
                        help="Specifies epitope prediction threshold for SYFPEITHI (default 20).")

    parser.add_argument("-o", "--output",
                        required=True,
                        help="Specifies the output file.")
    parser.add_argument("-t", "--threads",
                        type=int,
                        default=None,
                        help="Specifies number of threads. If not specified all available logical cpus are used.")


    args = parser.parse_args()

    #parse input
    peptides = list(FileReader.read_lines(args.input, type=Peptide))
    #read in alleles
    alleles = generate_alleles(args.alleles)

    if args.cleavage_prediction.upper() not in ["PCM", "PROTEASMM_C", "PROTEASMM_S"]:
        print "Specified cleavage predictor is currently not supported. Please choose either PCM, PROTEASMM_C, or PROTEASMM_S"
        sys.exit(-1)

    if args.epitope_prediction.upper() not in ["SYFPEITHI", "BIMAS", "SMM", "SMMPMBEC"]:
        print "Specified cleavage predictor is currently not supported. Please choose either Syfpeithi, BIMAS, SMM, SMMPMBEC"
        sys.exit(-1)

    #set-up model
    cl_pred = CleavageSitePredictorFactory(args.cleavage_prediction)
    epi_pred = EpitopePredictorFactory(args.epitope_prediction)

    if args.threshold == 0:
        pass
    elif args.epitope_prediction in ["SMM","SMMPMBEC"]:
        args.threshold = -math.log(args.threshold, 10)
    elif args.epitope_prediction == "BIMAS":
        args.threshold = math.log(args.threshold, math.e)


    thr = {a.name:args.threshold for a in alleles}

    solver = EpitopeAssemblyWithSpacer(peptides,cl_pred,epi_pred,alleles,
                                       k=args.max_length,en=9,threshold=thr,
                                       solver="cplex", alpha=args.alpha, beta=args.beta,
                                       verbosity=0)

    #solve
    #pre-processing has to be disable otherwise many solver will destroy the symmetry of the problem
    #how to do this is dependent on the solver used. For CPLEX it is preprocessing_presolve=n
    threads = mp.cpu_count() if args.threads is None else args.threads
    svbws = solver.approximate(threads=threads,options="preprocessing_presolve=n,threads=1")

    print
    print "Resulting String-of-Beads: ","-".join(map(str,svbws))
    print
    with open(args.output, "w") as f:
        f.write("-".join(map(str,svbws)))


if __name__ == "__main__":
    main()
