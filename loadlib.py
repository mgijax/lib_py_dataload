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

logicalDBDict = {}	# logical DB
mgiTypeDict = {}	# mgi type
markerDict = {}      	# markers
objectDict = {}		# objects
probeDict = {}		# probes
referenceDict = {}      # references
termDict = {}		# terms
userDict = {}		# users
markerTypeDict = {}	# marker types

loaddate = mgi_utils.date('%m/%d/%Y')	# current date

# Purpose: verifies the Logical DB value
# Returns: 0 if the Logical DB value does not exist in MGI
#          else the primary key of the Logical DB
# Assumes: nothing
# Effects: initializes the Logical DB dictionary for quicker lookup
# Throws: nothing

def verifyLogicalDB(
    logicalDB,   # the Logical DB value from the input file (string)
    lineNum,     # the line number (from the input file) on which this value was found (integer)
    errorFile    # error file
    ):

    global logicalDBDict

    if len(logicalDBDict) == 0:
        results = db.sql('select _LogicalDB_key, name from ACC_LogicalDB', 'auto')
        for r in results:
            logicalDBDict[r['name']] = r['_LogicalDB_key']

    if logicalDBDict.has_key(logicalDB):
        logicalDBKey = logicalDBDict[logicalDB]
    else:
	if errorFile != None:
            errorFile.write('Invalid Logical DB (%d): %s\n' % (lineNum, logicalDB))
        logicalDBKey = 0

    return logicalDBKey

# Purpose:  verify Marker Accession ID
# Returns:  Marker Key if Marker is valid, else 0
# Assumes:  Organism is "mouse"
# Effects:  verifies that the Marker exists either in the Marker dictionary or the database
#	writes to the error file if the Marker is invalid
#	adds the Marker id and key to the Marker dictionary if the Marker is valid
# Throws:  nothing

def verifyMarker(
    markerID, 	# Accession ID of the Marker (string)
    lineNum,	# line number (integer)
    errorFile,  # error file descriptor
    checkDuplicate = 0,	# check if Marker is a duplicate
    organism = 'mouse, laboratory'
    ):

    global markerDict

    markerKey = 0

    if markerDict.has_key(markerID):
	if checkDuplicate:
	    if errorFile != None:
		errorFile.write('Duplicate Mouse Marker (%d) %s\n' % (lineNum, markerID))
        else:
	    markerKey = markerDict[markerID]
    else:
        results = db.sql('select a._Object_key ' + \
	    'from MRK_Acc_View a, MRK_Marker m, MRK_Species s ' + \
	    'where a.accID = "%s" ' % (markerID) + \
	    'and a._Object_key = m._Marker_key ' + \
	    'and m._Species_key = s._Species_key ' + \
	    'and s.name = "%s" ' % (organism), 'auto')

#        results = db.sql('select a._Object_key ' + \
#	    'from MRK_Acc_View a, MRK_Marker m, MGI_Organism o ' + \
#	    'where a.accID = "%s" ' % (markerID) + \
#	    'and a._Object_key = m._Marker_key ' + \
#	    'and m._Organism_key = o._Organism_key ' + \
#	    'and o.commonName = "%s" ' % (organism), 'auto')

        for r in results:
            if r['_Object_key'] is None:
		if errorFile != None:
                    errorFile.write('Invalid Marker (%d) %s\n' % (lineNum, markerID))
                markerKey = 0
            else:
                markerKey = r['_Object_key']
		markerDict[markerID] = markerKey

    return markerKey

# Purpose: verifies the MGI Type value
# Returns: 0 if the MGI Type value does not exist in MGI
#          else the primary key of the MGI Type
# Assumes: nothing
# Effects: initializes the MGI Type dictionary for quicker lookup
# Throws: nothing

def verifyMGIType(
    mgiType,	 # the MGI Type value from the input file (string)
    lineNum,     # the line number (from the input file) on which this value was found (integer)
    errorFile    # error file
    ):

    global mgiTypeDict

    if len(mgiTypeDict) == 0:
        results = db.sql('select _MGIType_key, name from ACC_MGIType', 'auto')
        for r in results:
            mgiTypeDict[r['name']] = r['_MGIType_key']

    if mgiTypeDict.has_key(mgiType):
        mgiTypeKey = mgiTypeDict[mgiType]
    else:
	if errorFile != None:
            errorFile.write('Invalid MGI Type (%d): %s\n' % (lineNum, mgiType))
        mgiTypeKey = 0

    return mgiTypeKey

# Purpose:  verify Object Accession ID
# Returns:  Object Key if Object is valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Object exists either in the Object dictionary or the database
#	by either the Object ID or the Object Description
#	writes to the error file if the Object is invalid
#	adds the Object id and key to the Object dictionary if the Object is valid
# Throws:  nothing

def verifyObject(
    objectID, 		# Accession ID of the Object (string)
    mgiTypeKey, 	# Object Type (string)
    objectDescription,	# Object description (string)
    lineNum,		# line number (integer)
    errorFile   	# error file descriptor
    ):

    global objectDict

    objectKey = None

    if len(objectID) > 0 and objectDict.has_key(objectID):
        return objectDict[objectID] 

    elif len(objectID) > 0:
        results = db.sql('select a._Object_key from ACC_Accession a ' + \
            'where a.accID = "%s" ' % (objectID) + \
            'and a._MGIType_key = %s' % (mgiTypeKey), 'auto')

        for r in results:
            objectKey = r['_Object_key']
    else:
        results = db.sql('select dbView from ACC_MGIType where _MGIType_key = %s' % (mgiTypeKey), 'auto')

	if len(results) > 0:
            dbView = results[0]['dbView']

            results = db.sql('select _Object_key from %s ' % (dbView) + \
	        ' where description = "%s" ' % (objectDescription), 'auto')

            for r in results:
                objectKey = r['_Object_key']

    if objectKey is None:
	if errorFile != None:
            errorFile.write('Invalid Object (%d) %s\n' % (lineNum, objectID))
        objectKey = 0
    else:
        objectDict[objectID] = objectKey

    return objectKey

# Purpose:  verify Probe Accession ID
# Returns:  Probe Key if Probe is valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Probe exists either in the Probe dictionary or the database
#	writes to the error file if the Probe is invalid
#	adds the Probe id and key to the Probe dictionary if the Probe is valid
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
		if errorFile != None:
                    errorFile.write('Invalid Mouse Probe (%d) %s\n' % (lineNum, probeID))
                probeKey = 0
            else:
                probeKey = r['_Object_key']
                probeDict[probeID] = probeKey

    return probeKey

# Purpose:  verify Reference Accession ID
# Returns:  Reference Key if Reference is valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Reference exists either in the Reference dictionary or the database
#	writes to the error file if the Reference is invalid
#	adds the Reference id and key to the Reference dictionary if the Reference is valid
# Throws:  nothing

def verifyReference(
    referenceID,        # reference accession ID (string)
    lineNum,		# line number (integer)
    errorFile   	# error file descriptor
    ):

    global referenceDict

    if referenceDict.has_key(referenceID):
        referenceKey = referenceDict[referenceID]
    else:
        referenceKey = accessionlib.get_Object_key(referenceID, 'Reference')
        if referenceKey is None:
	    if errorFile != None:
                errorFile.write('Invalid Reference (%d): %s\n' % (lineNum, referenceID))
            referenceKey = 0
        else:
            referenceDict[referenceID] = referenceKey

    return referenceKey

# Purpose:  verify Term Accession ID
# Returns:  Term Key if Term is valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Term exists either in the Term dictionary or the database
#	by either the Term ID or the Term Description/Term Vocabulary
#	writes to the error file if the Term is invalid
#	adds the Term id and key to the Term dictionary if the Term is valid
# Throws:  nothing

def verifyTerm(
    termID, 		# Accession ID of the Term (string)
    vocabKey,		# Vocabulary key (string)
    termDescription,	# Term description (string)
    lineNum,		# line number (integer)
    errorFile   	# error file descriptor
    ):

    global termDict

    termKey = None

    if len(termID) > 0 and termDict.has_key(termID):
        return termDict[termID] 

    elif len(termID) > 0:
        results = db.sql('select a._Object_key from VOC_Term_Acc_View a ' + \
            'where a.accID = "%s" ' % (termID), 'auto')

        for r in results:
            termKey = r['_Object_key']
    else:
        results = db.sql('select _Term_key from VOC_Term ' + \
		'where term = "%s" ' % (termDescription) + \
		'and _Vocab_key = %s' % (vocabKey), 'auto')

        for r in results:
            termKey = r['_Term_key']

    if termKey is None:
	if errorFile != None:
            errorFile.write('Invalid Term (%d) %s\n' % (lineNum, termID))
        termKey = 0
    else:
        termDict[termID] = termKey

    return termKey

def verifyUser(
    userID, 	# User ID (string)
    lineNum,	# line number (integer)
    errorFile   # error file descriptor
    ):

    global userDict

    if len(userDict) == 0:
        results = db.sql('select _User_key, login from MGI_User_Active_View', 'auto')
        for r in results:
            userDict[r['login']] = r['_User_key']

    if userDict.has_key(userID):
        userKey = userDict[userID]
    else:
	if errorFile != None:
            errorFile.write('Invalid User (%d): %s\n' % (lineNum, userID))
        userKey = 0

    return userKey

# Purpose:  verify Marker Type
# Returns:  Marker Type key if valid, else 0
# Assumes:  nothing
# Effects:  verifies that the Marker Type exists in the markerType dictionary
#	writes to the error file if the Marker Type is invalid
# Throws:  nothing

def verifyMarkerType(
    markerType, 	  # Marker Type value (string)
    lineNum,	  # line number (integer)
    errorFile	   # error file (file descriptor)
    ):

    global markerTypeDict

    markerTypeKey = 0

    if len(markerTypeDict) == 0:
        results = db.sql('select _Marker_Type_key, name from MRK_Types', 'auto')
	for r in results:
	    markerTypeDict[r['name']] = r['_Marker_Type_key']

    if markerTypeDict.has_key(markerType):
        markerTypeKey = markerTypeDict[markerType]
    else:
	if errorFile != None:
            errorFile.write('Invalid Marker Type (%d): %s\n' % (lineNum, markerType))

    return markerTypeKey

# $Log$
# Revision 1.5  2003/09/25 13:04:45  lec
# new
#
# Revision 1.4  2003/09/25 12:40:30  lec
# new
#
# Revision 1.3  2003/09/25 12:11:48  lec
# new
#
# $Log$
# Revision 1.5  2003/09/25 13:04:45  lec
# new
#
# Revision 1.4  2003/09/25 12:40:30  lec
# new
#
# Revision 1.3  2003/09/25 12:11:48  lec
# new
#
# Revision 1.2  2003/09/24 17:35:25  lec
# new
#
# Revision 1.1  2003/09/23 19:44:16  lec
# new
#
