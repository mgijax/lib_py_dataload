#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: vocabloadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any VOC data load can use.
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
import string
import db
import mgi_utils
import accessionlib

#globals

ecodeDict = {}         # evidence codes

# Purpose:  verify Evidence Code
# Returns:  Evidence Code key if valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Evidence Code exists in the ecode dictionary
#	writes to the error file if the Evidence Code is invalid
# Throws:  nothing

def verifyEvidence(
    ecode, 	  # Evidence Code value (string)
    annotTypeKey, # Annotation Type key, (string)
    lineNum,	  # line number (integer)
    errorFile	   # error file (file descriptor)
    ):

    global ecodeDict

    ecodeKey = 0

    if len(ecodeDict) == 0:
        results = db.sql('select e._Term_key, e.abbreviation ' + \
                        'from VOC_Term e, VOC_AnnotType t ' + \
                        'where e._Vocab_key = t._EvidenceVocab_key ' + \
                        'and t._AnnotType_key = %s\n' % (annotTypeKey), 'auto')

	for r in results:
	    ecodeDict[r['abbreviation']] = r['_Term_key']

    if ecodeDict.has_key(ecode):
        ecodeKey = ecodeDict[ecode]
    else:
        errorFile.write('Invalid Evidence Code (%d): %s\n' % (lineNum, ecode))

    return ecodeKey

# $Log$
#
