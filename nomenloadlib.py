#!/usr/local/bin/python

#
# Program: nomenloadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any Nomen data load can use.
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

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db

except:
    import db

#globals

nomenStatusDict = {}         # nomen status

# Purpose:  verify Nomen Status
# Returns:  Nomen Status key if valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Nomen Status exists in the status dictionary
#	writes to the error file if the Nomen Status is invalid
# Throws:  nothing

def verifyNomenStatus(
    status, 	  # Nomen Status value (string)
    lineNum,	  # line number (integer)
    errorFile	   # error file (file descriptor)
    ):

    global nomenStatusDict

    statusKey = 0

    if len(nomenStatusDict) == 0:
        results = db.sql('select _Term_key, term from VOC_Term_NomenStatus_View', 'auto')
	for r in results:
	    nomenStatusDict[r['term']] = r['_Term_key']

    if nomenStatusDict.has_key(status):
        statusKey = nomenStatusDict[status]
    else:
	if errorFile != None:
            errorFile.write('Invalid Nomen Status (%d): %s\n' % (lineNum, status))

    return statusKey

