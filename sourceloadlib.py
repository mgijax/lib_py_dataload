#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: sourceloadlib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Provide a set of library functions that any Source (PRB_Source) data load can use.
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
import agelib

#globals

cellLineDict = {}
genderDict = {}		# dictionary of Gender
libraryDict = {}        # dictionary of Library names and Library keys
libraryIDDict = {}      # dictionary of Library Ids and Library keys
organismDict = {}	# dictionary of Organisms and keys
segmentTypeDict = {}	# dictionary of Segment Types and keys
sourceDict = {}		# dictionary of Source and keys
strainDict = {}         # dictionary of Strain names and Strain keys
tissueDict = {}         # dictionary of Tissue names and Tissue keys
vectorTypeDict = {}	# dictionary of Vector Types and keys

genderList = ['Female', 'Male', 'Pooled', 'Not Specified']      # list of valid Gender values

# Purpose: verifies the age value
# Returns: ageMin, ageMax; the numeric values which correspond to the age
# Assumes: nothing
# Effects: writes to the error log if the age is invalid
# Throws: nothing

def verifyAge(
    age,         # the Age value from the input file (string)
    lineNum,     # the line number (from the input file) on which this value was found (integer)
    errorFile	 # error file (file descriptor)
    ):

    ageMin, ageMax = agelib.ageMinMax(age)

    if ageMin == -1.0:
	if errorFile != None:
            errorFile.write('Invalid Age (line: %d) %s\n' % (lineNum, age))

    return ageMin, ageMax 

# Purpose: verifies the Cell Line
# Returns: 0 if the Cell Line
#		else the primary key of the Cell Line
# Assumes: nothing
# Effects: saves the Cell Line/primary key in a dictionary for faster lookup
#          writes to the error log if the Cell Line is invalid
# Throws: nothing

def verifyCellLine(
    cellLine,	# the Cell Line value from the input file (string)
    lineNum,	# the line number (from the input file) on which this value was found
    errorFile	# error file (file descriptor)
    ):

    global cellLineDict

    if len(cellLineDict) == 0:
        results = db.sql('select _Term_key, term from VOC_Term_CellLine_View', 'auto')
        for r in results:
            cellLineDict[r['term']] = r['_Term_key']

    if cellLineDict.has_key(cellLine):
        return cellLineDict[cellLine]
    else:
	if errorFile != None:
            errorFile.write('Invalid Cell Line (line: %d) %s\n' % (lineNum, cellLine))
        return 0

# Purpose: verifies the Library value
# Returns: 0 if the Library does not exist in MGI
#          else the primary key of the Library
# Assumes: nothing
# Effects: initializes the Library dictionary for quicker lookup
# Throws: nothing

def verifyLibrary(
    libraryName, # the Library Name value from the input file (string)
    lineNum,     # the line number (from the input file) on which this value was found (integer)
    errorFile = None	# error file (file descriptor)
    ):

    global libraryDict

    # if dictionary is empty, initialize it
    if len(libraryDict) == 0:
        results = db.sql('select _Source_key, name from PRB_Source where name is not null', 'auto')
        for r in results:
            libraryDict[r['name']] = r['_Source_key']

    if libraryDict.has_key(libraryName):
        return libraryDict[libraryName] 
    else:
	if errorFile != None:
            errorFile.write('Invalid Library (line: %d) %s\n' % (lineNum, libraryName))
        return 0

# Purpose: verifies the Library value by ID
# Returns: 0 if the Library does not exist in MGI
#          else the primary key of the Library
# Assumes: nothing
# Effects: initializes the Library dictionary for quicker lookup
# Throws: nothing

def verifyLibraryID(
    libraryID,   # the Library ID value from the input file (string)
    logicalDBKey,# the Logical DB key value of the Library from the input file (string)
    lineNum,     # the line number (from the input file) on which this value was found (integer)
    errorFile = None	# error file (file descriptor)
    ):

    global libraryIDDict

    # if dictionary is empty, initialize it
    if len(libraryIDDict) == 0:
        results = db.sql('select _LogicalDB_key, _Object_key, accID from PRB_Source_Acc_View', 'auto')
        for r in results:
	    key = str(r['_LogicalDB_key']) + ':' + r['accID']
	    value = r['_Object_key']
            libraryIDDict[key] = value

    key = str(logicalDBKey) + ':' + libraryID
    if libraryIDDict.has_key(key):
        return libraryIDDict[key] 
    else:
	if errorFile != None:
            errorFile.write('Invalid Library ID (line: %d) %s\n' % (lineNum, libraryID))
        return 0

# Purpose: verifies the Gender
# Returns: 0 if the Gender
#		else the primary key of the Gender
# Assumes: nothing
# Effects: saves the Gender/primary key in a dictionary for faster lookup
#          writes to the error log if the Gender is invalid
# Throws: nothing

def verifyGender(
    gender,	# the Gender value from the input file (string)
    lineNum,	# the line number (from the input file) on which this value was found
    errorFile	# error file (file descriptor)
    ):

    global genderDict

    if len(genderDict) == 0:
        results = db.sql('select _Term_key, term from VOC_Term_Gender_View', 'auto')
        for r in results:
            genderDict[r['term']] = r['_Term_key']

    if genderDict.has_key(gender):
        return genderDict[gender]
    else:
	if errorFile != None:
            errorFile.write('Invalid Gender (line: %d) %s\n' % (lineNum, gender))
        return 0

# Purpose: verifies the Organism
# Returns: 0 if the Organism
#		else the primary key of the Organism
# Assumes: nothing
# Effects: saves the Organism/primary key in a dictionary for faster lookup
#          writes to the error log if the Organism is invalid
# Throws: nothing

def verifyOrganism(
    organism,		# the Organism value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global organismDict

    if organismDict.has_key(organism):
        return organismDict[organism] 
    else:
        results = db.sql('select _Organism_key from MGI_Organism where commonName = "%s"' % (organism), 'auto')

	if len(results) == 0:
	    if errorFile != None:
                errorFile.write('Invalid Organism (line: %d) %s\n' % (lineNum, organism))
	    return 0

        for r in results:
            organismDict[organism] = r['_Organism_key']
            return r['_Organism_key'] 

# Purpose: verifies the Sex
# Returns: 0 if the Sex value is invalid
#		else the Sex value
# Assumes: nothing
# Effects: writes to the error log if the Sex is invalid
# Throws: nothing

def verifySex(
    gender, 		# the Sex value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found (integer)
    errorFile	 # error file (file descriptor)
    ):

    if gender in genderList:
        return gender 
    else:
	if errorFile != None:
            errorFile.write('Invalid Gender (line: %d): %s\n' % (lineNum, gender))
        return 0

# Purpose: verifies the Source
# Returns: 0 if the Source
#		else the primary key of the Source
# Assumes: nothing
# Effects: saves the Source/primary key in a dictionary for faster lookup
#          writes to the error log if the Source is invalid
# Throws: nothing

def verifySource(
    segmentTypeKey, 
    vectorKey, 
    organismKey, 
    strainKey, 
    tissueKey, 
    genderKey, 
    cellLineKey, 
    age,
    lineNum,	# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global sourceDict

    source = "%s,%s,%s,%s,%s,%s,%s,%s" % (segmentTypeKey, vectorKey, organismKey, strainKey, tissueKey, genderKey, cellLineKey, age)

    if sourceDict.has_key(source):
        return sourceDict[source] 
    else:
        results = db.sql('select _Source_key from PRB_Source where ' + \
		'_SegmentType_key = %s ' % (segmentTypeKey) + \
		'and _Vector_key = %s ' % (vectorKey) + \
		'and _Organism_key = %s ' % (organismKey) + \
		'and _Strain_key = %s ' % (strainKey) + \
		'and _Tissue_key = %s ' % (tissueKey) + \
		'and _Gender_key = %s ' % (genderKey) + \
		'and _CellLine_key = %s ' % (cellLineKey) + \
		'and age = "%s" ' % (age) + \
		'and isCuratorEdited = 0 ', 'auto')

	if len(results) == 0:
	    if errorFile != None:
                errorFile.write('Invalid Source (line: %d) %s\n' % (lineNum, source))
	    return 0

        for r in results:
            sourceDict[source] = r['_Source_key']
            return r['_Source_key'] 

# Purpose: verifies the Strain
# Returns: 0 if the Strain
#		else the primary key of the Strain
# Assumes: nothing
# Effects: saves the Strain/primary key in a dictionary for faster lookup
#          writes to the error log if the Strain is invalid
# Throws: nothing

def verifyStrain(
    strain,		# the Strain value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global strainDict

    if strainDict.has_key(strain):
        return strainDict[strain] 
    else:
        results = db.sql('select s._Strain_key ' + \
            'from PRB_Strain s ' + \
            'where s.strain = "%s" ' % (strain), 'auto')

	if len(results) == 0:
	    if errorFile != None:
                errorFile.write('Invalid Strain (line: %d) %s\n' % (lineNum, strain))
	    return 0

        for r in results:
            strainDict[strain] = r['_Strain_key']
            return r['_Strain_key'] 

# Purpose: verifies the Tissue
# Returns: 0 if the Tissue
#		else the primary key of the Tissue
# Assumes: nothing
# Effects: saves the Tissue/primary key in a dictionary for faster lookup
#          writes to the error log if the Tissue is invalid
# Throws: nothing

def verifyTissue(
    tissue,		# the Tissue value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global tissueDict

    if len(tissueDict) == 0:
        results = db.sql('select _Tissue_key, tissue from PRB_Tissue ', 'auto')
        for r in results:
            tissueDict[r['tissue']] = r['_Tissue_key']

    if tissueDict.has_key(tissue):
        return tissueDict[tissue]
    else:
	if errorFile != None:
            errorFile.write('Invalid Tissue (line: %d) %s\n' % (lineNum, tissue))
        return 0

# Purpose: verifies the Segment Type
# Returns: 0 if the Segment Type
#		else the primary key of the Segment Type
# Assumes: nothing
# Effects: saves the Segment Type/primary key in a dictionary for faster lookup
#          writes to the error log if the Segment Type is invalid
# Throws: nothing

def verifySegmentType(
    segmentType,	# the SegmentType value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global segmentTypeDict

    if len(segmentTypeDict) == 0:
        results = db.sql('select _Term_key, term from VOC_Term_SegmentType_View', 'auto')
        for r in results:
            segmentTypeDict[r['term']] = r['_Term_key']

    if segmentTypeDict.has_key(segmentType):
        return segmentTypeDict[segmentType]
    else:
	if errorFile != None:
            errorFile.write('Invalid SegmentType (line: %d) %s\n' % (lineNum, segmentType))
        return 0

# Purpose: verifies the Vector Type
# Returns: 0 if the Vector Type
#		else the primary key of the Vector Type
# Assumes: nothing
# Effects: saves the Vector Type/primary key in a dictionary for faster lookup
#          writes to the error log if the Vector Type is invalid
# Throws: nothing

def verifyVectorType(
    vectorType,		# the VectorType value from the input file (string)
    lineNum,		# the line number (from the input file) on which this value was found
    errorFile	 # error file (file descriptor)
    ):

    global vectorTypeDict

    if len(vectorTypeDict) == 0:
        results = db.sql('select _Term_key, term from VOC_Term_SegVectorType_View', 'auto')
        for r in results:
            vectorTypeDict[r['term']] = r['_Term_key']

    if vectorTypeDict.has_key(vectorType):
        return vectorTypeDict[vectorType]
    else:
	if errorFile != None:
            errorFile.write('Invalid VectorType (line: %d) %s\n' % (lineNum, vectorType))
        return 0

# $Log$
# Revision 1.8  2005/06/30 13:36:17  lec
# fix verifyAge
#
# Revision 1.7  2004/08/27 18:57:20  lec
# TR6118
#
# Revision 1.6  2004/08/23 16:11:26  lec
# JSAM
#
# Revision 1.5  2004/01/14 20:25:05  lec
# fix
#
# Revision 1.4  2004/01/14 20:23:56  lec
# fix
#
# Revision 1.3  2004/01/14 20:23:38  lec
# fix
#
# Revision 1.2  2004/01/14 18:49:35  lec
# updated
#
# Revision 1.1  2003/09/25 12:40:32  lec
# new
#
#
