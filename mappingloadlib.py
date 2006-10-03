#!/usr/local/bin/python

#
# Program: mappingloadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any Mapping data load can use.
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

import sys
import os
import db

#globals

assayDict = {}         # mapping assay

# Purpose:  verify Mapping Assay
# Returns:  Mapping Assay key if valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Mapping Assay exists in the Assay dictionary
#	writes to the error file if the Mapping Assay is invalid
# Throws:  nothing

def verifyAssay(
    assay, 	  # Mapping Assay value (string)
    lineNum,	  # line number (integer)
    errorFile	  # error file (file descriptor)
    ):

    global assayDict

    assayKey = 0

    if len(assayDict) == 0:
        results = db.sql('select _Assay_Type_key, description from MLD_Assay_Types', 'auto')
	for r in results:
	    assayDict[r['description']] = r['_Assay_Type_key']

    if assayDict.has_key(assay):
        assayKey = assayDict[assay]
    else:
	if errorFile != None:
            errorFile.write('Invalid Mapping Assay (%d): %s\n' % (lineNum, assay))

    return assayKey

