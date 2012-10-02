#!/usr/local/bin/python

#
# Program: alleleloadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any Allele data load can use
#
# Requirements Satisfied by This Program:
#
# Usage:
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
# 10/02/2012	lec
#	- TR10273/High Throughput Phenotypes/Sanger
#

import sys
import os
import db

#globals

mutantCellLineDict = {}      # mutant cell line

# Purpose:  verify Mutant Cell Line
# Returns:  Mutant Cell Line key if valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Mutant Cell Line exists in the Mutant Cell Line dictionary
#	writes to the error file if the Mutant Cell Line is invalid
# Throws:  nothing

def verifyMutnatCellLine(
    mutantCellLine, 	# Mutant Clel Line value (string)
    lineNum,		# line number (integer)
    errorFile	   	# error file (file descriptor)
    ):

    global mutantCellLineDict

    mutantCellLineKey = 0

    if len(mutantCellLineDict) == 0:
	results = db.sql('''
		select _CellLine_key, cellLine 
		from ALL_CellLine
		where cellLine = '%s'
		and isMutant = 1
		''' % (mutantCellLine), 'auto')
	for r in results:
	    mutantCellLineDict[r['cellLine']] = r['_CellLine_key']

    if mutantCellLineDict.has_key(mutantCellLine):
        mutantCellLineKey = mutantCellLineDict[mutantCellLine]
    else:
	if errorFile != None:
            errorFile.write('Invalid Mutant Cell Line (%d): %s\n' % (lineNum, mutantCellLine))

    return mutantCellLineKey

