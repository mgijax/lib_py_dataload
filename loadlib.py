#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: loadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any data load can use.
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

markerDict = {}      	# dictionary of markers for quick lookup
probeDict = {}		# dictionary of probes for quick lookup
referenceDict = {}      # dictionary of references for quick lookup
userDict = {}		# dictionary of users for quick lookup

loaddate = mgi_utils.date('%m/%d/%Y')	# current date

def verifyMarker(
    markerID, 	# Accession ID of the Marker (string)
    lineNum,	# line number (integer)
    errorFile   # error file descriptor
    ):

    global markerDict

    markerKey = 0

    if markerDict.has_key(markerID):
        markerKey = markerDict[markerID]
    else:
        results = db.sql('select _Object_key from MRK_Acc_View where accID = "%s" ' % (markerID), 'auto')

        for r in results:
            if r['_Object_key'] is None:
                errorFile.write('Invalid Marker (%d) %s\n' % (lineNum, markerID))
                markerKey = 0
            else:
                markerKey = r['_Object_key']
		markerDict[markerID] = markerKey

    return markerKey

# Purpose:  verify Probe Accession ID
# Returns:  Probe Key if Probe is valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Probe exists either in the probe dictionary or the database
#	writes to the error file if the Probe is invalid
#	adds the probe id and key to the probe dictionary if the Probe is valid
# Throws:  nothing

def verifyProbe(
    probeID, 	# Accession ID of the Probe (string)
    lineNum,	# line number (integer)
    errorFile   # error file (file descriptor)
    ):

    global probeDict

    probeKey = 0

    if probeDict.has_key(probeID):
        return probeDict[probeID]
    else:
        results = db.sql('select _Object_key from PRB_Acc_View where accID = "%s" ' % (probeID), 'auto')

        for r in results:
            if r['_Object_key'] is None:
                errorFile.write('Invalid Mouse Probe (%d) %s\n' % (lineNum, probeID))
                probeKey = 0
            else:
                probeKey = r['_Object_key']
                probeDict[probeID] = probeKey

    return probeKey

def verifyReference(
    referenceID,        # reference accession ID; J:#### (string)
    lineNum,		# line number (integer)
    errorFile   	# error file descriptor
    ):

    global referenceDict

    if referenceDict.has_key(referenceID):
        referenceKey = referenceDict[referenceID]
    else:
        referenceKey = accessionlib.get_Object_key(referenceID, 'Reference')
        if referenceKey is None:
            errorFile.write('Invalid Reference (%d): %s\n' % (lineNum, referenceID))
            referenceKey = 0
        else:
            referenceDict[referenceID] = referenceKey

    return referenceKey

def verifyUser(
    userID, 	# User ID (string)
    lineNum,	# line number (integer)
    errorFile   # error file descriptor
    ):

    global userDict

    if len(userDict) == 0:
        results = db.sql('select _User_key, login from MGI_User', 'auto')
        for r in results:
            userDict[r['login']] = r['_User_key']

    if userDict.has_key(userID):
        userKey = userDict[userID]
    else:
        errorFile.write('Invalid User (%d): %s\n' % (lineNum, userID))
        userKey = 0

    return userKey

# $Log$
