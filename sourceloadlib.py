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
segmentTypeDict = {}	# dictionary of Segment Types and keys
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

    if ageMin == None:
        ageMin = -1
        ageMax = -1

    if ageMin == None:
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
    lineNum      # the line number (from the input file) on which this value was found (integer)
    ):

    global libraryDict

    # if dictionary is empty, initialize it
    if len(libraryDict) == 0:
        results = db.sql('select _Source_key, name from %s where name is not null' % (libraryTable), 'auto')
        for r in results:
            libraryDict[r['name']] = r['_Source_key']

    if libraryDict.has_key(libraryName):
        return libraryDict[libraryName] 
    else:
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
        results = db.sql('select _Vector_key, vectorType from PRB_VectorTypes ', 'auto')
        for r in results:
            vectorTypeDict[r['vectorType']] = r['_Vector_key']

    if vectorTypeDict.has_key(vectorType):
        return vectorTypeDict[vectorType]
    else:
	if errorFile != None:
            errorFile.write('Invalid VectorType (line: %d) %s\n' % (lineNum, vectorType))
        return 0

# $Log$
#
