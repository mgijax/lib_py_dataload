#! /usr/local/bin/python

############################################################################
#
#  Author:    R. Palazola
#  Date:    11/97
#  Purpose: 
#    Provide utility services for programs that need 
#	- to generage primary keys for int-keyed tables.
#	- to generate accession key sequences,
#	- to generate MGI accession number sequences,
#	- Foreign Key look ups (translate between a value and its db key)
#
#    especially for bulk processing where many such IDs would be generated.
#    As logical DBs and MGITypes are pertinent to accession numbers, objects
#   and interface functions are are provided for these tables in the db as 
#   well.
#
#    This is a second generation version, that uses an interface function style
#    to access the provided services which are implemented in underlying objects;
#   it also provides generic instantiate-able classes for those look-up and
#   sequence services _not_ provided as objects in this library.
#
############################################################################
# Copyright (C) 1997 The Jackson Laboratory
#
# Permission to use, copy, modify, distribute, and sell this software
# and its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, that the fact that modifications have
# been made is clearly represented in any modified copies, and that
# the name of The Jackson Laboratory not be used in advertising or
# publicity pertaining to distribution of the software without
# specific, written prior permission.
#  
# THE JACKSON LABORATORY MAKES NO REPRESENTATIONS ABOUT THE
# SUITABILITY OF THIS SOFTWARE FOR ANY PURPOSE AND MAKES NO
# WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING WARRANTIES
# OF MERCHANTABILITY OR FITNESS OR THAT THE USE OF THIS
# SOFTWARE WILL NOT INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS,
# TRADEMARKS OR OTHER RIGHTS.  IT IS PROVIDED "AS IS."
#
############################################################################

# """
#     INTRODUCTION/DESCRIPTION:
#   Utility module used by various load and migration scripts to control 
#     assigning MGI: numbers and _Accession_key ids and providing translation
#   tables for _MGITypes and _LogicalDBs for working with accession numbers.
#
#   The module implements a "public" interface via a set of functions
#   which is the recommended and preferred method of access.  It is NOT
#   recommended that a user instantiate any of the internal objects.  
#   Mis-use can at best result in ineffeciencies, and at worst generating
#   duplicate accession keys or MGI accession numbers.
#
#   As an alternative to directly instantiating objects in the module,
#   interface functions that return references to the internal class
#   objects are provided.  This is the prefered method for accessing
#   the individual objects in the module.  It is provided as a means
#   to access functionality NOT provided for in the public interface 
#   functions.  Obviously, accessing the underlying objects requires
#   the programmer become familiar with the internals of these classes.
#   This mechanism does not protect the programmer from misuse or 
#   misunderstanding these objects.  It limits instantiation to single 
#   instances of each object while providing both full object-style
#   access and "backwards compatibility" for modules written using an
#   earlier version of this library.
#
#     The look up tables provide case-insensitivity with the ability to use
#     either a function-call or dictionary look-up style when using the object 
#   through references.  They are included here because of their relationship 
#   to working with accession numbers for foreign logical dbs.
#
#     ASSUMES:
#   For accession number sequence, single user -- no one else is adding data 
#   to acc_accession or generating accession keys or mgi accession numbers
#   "off-line" while client script is running!!!
#
#     NOTES: 
#     1). This was written prior to Geoff's improvements to sybaselib, and has
#     not yet been modified to handle any raised exceptions; it depends on db 
#     which could manage that for us.
#
#     2). In all 4 classes I decided to implement the data as instance 
#   variables, even though conceptually only one instance of each class
#   is required (or desirable for the accession sequences).
#
#
#   USEAGE:
#   Module MUST be INITIALIZED by calling its init() function:
#
#   E.G.:
#   import accessionLoadUtils
#   accessionLoadUtils.init("MGD_DEV", "mgd", "mgd_public", "mgd")    # REQ'D!!!
#   
#**********************************************************************
# PUBLIC GENERIC CLASSES:
#**********************************************************************
#
# DBLookUp : Provides a generic way to load translation tables from the db;
#    these provide case insensitive, bi-directional translations.
#    strainLookUp = DBLookUp (
#			   "select _Strain_key, strain from PRB_Strain",
#			   <server>, <database>, <user>, <pwd> )
#
# PrimaryKeySequence : provides standardized method to get ongoing 
#    sequences of ints based on a starting value from the db.
#    strainKey = PrimaryKeySequence (
#			   "select max(_Strain_key) from PRB_Strain",
#			   <server>, <database>, <user>, <pwd> )
#    nextStrain = strainKey.getNextKey()
#
#**********************************************************************
# PUBLIC INTERFACE FUNCTIONS:
#----------------------------------------------------------------------
#   Translation Interface Functions:
#----------------------------------------------------------------------
#     LogicalDB look ups:
#----------------------------------------------------------------------
# init ( server, database, user, password (all as string), mgiAcc as boolean )
#     -- returns a success/fail flag as an int, creating the sole instances of 
#    the objects that provide these services.  The mgiAcc flag indicates whether
#    or not the user wants mgi accession numbers initialized.
#
# getLogicalDBKey ( name as string ) : returns an int, the key for the name;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# getLogicalDBName ( key as int ) : returns a string, the name for the key;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# getLogicalDBObject () : returns a reference to the module's object; useful
#    where user needs access to functionality in the underlying object and
#    the public interface functions don't provide what's needed.
#
# hasLogicalDBName ( name as string ) : returns 1 if name is valid; else 0;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# hasLogicalDBKey ( key as int ) : returns 1 if key is valid; else 0;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
#----------------------------------------------------------------------
#     MGITypes look ups:
#----------------------------------------------------------------------
# getMGITypeKey ( name as string ) : returns an int, the key;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# getMGITypeName ( key as int ) : returns an MGIType names as string
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# hasMGITypeName ( name as string ) : returns 1 if name is valid; else 0;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# hasMGITypeKey ( key as int ) : return 1 if key is valid; else 0;
#    raises a TypeError if wrong arg. type, else may indirectly raise
#    KeyError through dictionary access.
#
# getMGITypeObject () : returns a reference to the module's object; useful
#    where user needs access to functionality in the underlying object and
#    the public interface functions don't provide what's needed.
#
#----------------------------------------------------------------------
#   Accession Number Interface Functions:
#----------------------------------------------------------------------
# mkAccession () : returns a list of values suitable as bcp input to the
#    ACC_Accession table (compatible w/ BCPWrite class).
#
#----------------------------------------------------------------------
#     Accession Key Interface Functions:
#----------------------------------------------------------------------
#
# getAccKeyObject () : returns a reference to the module's object; useful
#    where user needs access to functionality in the underlying object and
#    the public interface functions don't provide what's needed.
#
# getInitialAccKey () : returns the starting _Accession_key (int) which
#    will be the max(_Accession_key) in the database.
#
# getLastAccKey () : returns the last used _Accession_key (int); initially
#    same value as was loaded from the db.
#
# getNextAccKey () : consumes the next available _Accession_key and returns
#    it as an int.
#
# stillValidAccKey () : returns an int (0 or 1) indicating if the database
#    still has the same initial key as was loaded when the module 
#    initialized.
#
#----------------------------------------------------------------------
#     Mgi: Accession Key Interface Functions:
#----------------------------------------------------------------------
#
# getInitialMGIAcc () : returns the starting MGI Accession # (int) which
#    will be the last used MGI accession number in the db.
#
# getLastMGIAcc () : returns the last used MGI accession #; initially
#    values is same as was loaded from the db.
#
# getMGIAccObject () : returns a reference to the module's object; useful
#    where user needs access to functionality in the underlying object and
#    the public interface functions don't provide what's needed.
#
# getNextMGIAcc () : consumes the next available MGI accession # returning
#    it as an int.
#
# reserveMGIAcc () : attempts a safe write back to the database's 
#    ACC_AccessionMax table for the MGI accession number, returning a
#    success/fail flag indicating whether or not the update to the 
#    record in ACC_Accession Max succeeded.  The update statement
#    is structured in such a way that it will fail if the database
#    does not match the object's initial key value (self.initialKey).
#    
# stillValidMGIAcc () : returns a logical flag indicating if the
#    the database's MGI accession number is still consistent with
#    what was initially loaded.
#    WARNING: this is a slow operation, because the query is slow.
# 
#**********************************************************************
# INTERNAL CLASSES
#**********************************************************************
#
# LogicalDBLookUp : loads a look up table from the db  and provides look-up 
#    capability to return key values given a logical db name.
#
# MGITypeLookUp : loads a look up table from the db and provides look-up
#     capability to return key value given a MGIType name.
#
# AccKey : provides the next available _Accession_key value when program must
#     generate numerous new accession records.  Retrieves the information once,
#     then internally increments value for each value used.  NOTE: assumes 
#     single-user; does not repeatedly go back to the db to get the most current
#     next available key.
#
# MGIAccKey : provides similar capability for MGI accession numbers, with an
#   additional capability to "reserve" the consumed range of values by writing
#   the lastKey value back to the db.
#
# For AccKey and MGIAccKey, I specifically do not want the user to 
# instantiate different objects; the danger is that two objects would 
# supply duplicate values.  I specifically want any and all instances 
# within a programs execution to use the same object.
#
# Remember, the assumption is that the program is executing as if in 
# single user mode with regards the database's accession tables.
#
# For the two look-up utility classes, The data is a snap shoot of what's
# in the database; individual instances should all have the same 
# dictionaries, so loading duplicate copies is inefficient.
#
#----------------------------------------------------------------------
# ADDITIONAL FUNCTIONS:
#----------------------------------------------------------------------
# accSplit () : my version of a parser for accession numbers.  
#   Good candidate for consolidation with the standard accession library.
#
# sql (): wrapper for db.sql() that saves & restores login params
#----------------------------------------------------------------------
# DEPENDENCIES:
#----------------------------------------------------------------------
#    db.py (standard sybase access w/ sql() capability.)
#
#----------------------------------------------------------------------
# EXAMPLES (both simplistic):
#----------------------------------------------------------------------
#   Example using the public interface:
#
#   import accessionLoadUtils
#   # don't need the MGIAccession #'s, so pass optional, last arg 0/false:
#   accessionLoadUtils.init ( "MGD_DEV", "mgd", "mgd_public", "mgdpub", 0 )
#   segment = accessionLoadUtils.getMGITypeKey ( "Segment" )
#   dbEST = accessionLoadUtils.getLogicalDBKey ( "dbEST" )
#   dbESTAccID = "1234567"
#   (prefix, suffix) = accessionLoadUtils.accSplit ( dbESTAccID )
#     query = """insert into ACC_Accession (
#	_Accession_key, accID, prefixPart, numericPart, _LogicalDB_key
#	_Object_key, _MGIType_key, private, preferred,
#	creationDate, modificationDate, releaseDate )
#	values ( %u, '%s', '%s', %u, %s, %u, %u, 0, 1, , , )""" % ( 
#	       accessionLoadUtils.getNextAccKey(),   # next avail. _Accession_key
#	     dbESTaccID, # accID
#	     prefix,     # prefixPart
#	     suffix,     # numericPart
#	     dbEST,      # _logicalDB_key
#	     1234,       # _Object_key (arbitrary key to some relevant mgi obj.)
#	     segment     # _MGIType_key
#	 )
#
#
#----------------------------------------------------------------------
#    Example using the internal class objects:
#----------------------------------------------------------------------
#
#     import accessionLoadUtils
#
#     (server, db, user, pwd) = ("MGD_DEV", "mgd", "mgd_public", "mgdpub")
#
#   accessionLoadUtils.init (server, db, user, pwd)
#     mgiTypes = accessionLoadUtils.getMGITypeObject()
#     segment = mgiTypes("Segment")
#
#     logicalDBs = accessionLoadUtils.getLogicalDBObject()
#     dbEST = logicalDBs("dbEST")
#
#     accKey = accessionLoadUtils.getAccKeyObject()
#     mgiAccKey = accessionLoadUtils.getMGIAccObject()
#
#     dbESTaccID = "1234567"
#     (prefix, suffix) = accSplit ( dbESTaccID)
#     query = """insert into ACC_Accession (
#	_Accession_key, accID, prefixPart, numericPart, _LogicalDB_key
#	_Object_key, _MGIType_key, private, preferred,
#	creationDate, modificationDate, releaseDate )
#	values ( %u, '%s', '%s', %s, %u, %u, %u, 0, 1, , , )""" % ( 
#	       accKey.getNextKey(),   # next available _Accession_key
#	     dbESTaccID,	    # accID
#	     prefix,		# prefixPart
#	     suffix,		# numericPart
#	     dbEST,		 # _logicalDB_key
#	     1234,	  # _Object_key (arbitrary key to some relevant mgi object)
#	     segment		# _MGIType_key
#	 )
#
# (Actually, if I were attempting to do the above, I'd do it all in SQL.
# The more realistic example would be with an input file for which one had 
# to generate multiple accession records depending on what was in the input.)
#
#----------------------------------------------------------------------
# POSSIBLE IMPROVEMENTS:
#----------------------------------------------------------------------
# - Standardize on doc-string contents; there's some overhead to storing
#   all these strings as part of the class and function objects.
# - Adopt some standardized mechanism to pre-reserve MGI Accession numbers
#   and extend MGIAccKey to handle all declared reserved ranges.
#
#----------------------------------------------------------------------
# MODIFICATIONS:
#----------------------------------------------------------------------
#   01/12/2000 rpp:
#     - switched from mgdlib to db.py for sql()
#   12/17/1999 rpp:
#     - Corrections to class DBTranslationTable documentation
#   12/10/1999 rpp:
#     - reformatted smaller indent levels
#   2/18/98 rpp:
#     - renamed Accessionable to Sequencible, to include primary key sequences.
#     - added generic PrimaryKeySequence class.
#     - added optional step arg to Sequencible.getNextKey().
#     - relocated class DBLookUp code to new section for public, generic
#       classes.
#     - recoded method for handling unknown col. names in DBLookUp.__init__().
#     - added optional command line args to supply connect args when testing.
#   12/15-16/97 rpp:
#    - substituted mgdlib for sql library:
#	affecting MGITypeLookUp, LogicalDBLookUp, AccKey & MGIAccKey classes
#    12/3/97 rpp: 
#    - updated documentation.
#    - completed conversion away from class static data members.
#   12/2/97 rpp:
#    -   Extended MGIAccKey to track whether the values used is current w/ db.
# """


import regex, string, sys
from types import *

import db

# Module Globals:
# single instances of desired classes; initialized by init()
accKey = None
mgiAcc = None
logicalDBs = None
mgiTypes = None

NL = "\n"


#**********************************************************************
# BEGIN PUBLIC MODULE SERVICES:
#**********************************************************************

def init ( server, db, user, pwd, includeAcc = 1):
    """ initialize the module
    """
    #--------------------------------------------------
    # INPUTS:     
    #   server : string -- name of SQLServer
    #   db : string -- name of db
    #   user : string -- user ID
    #   pwd : string -- password
    #   includeAcc : int -- which Acc Objs to initialize -
    #		>0 includes both AccKey & mgiAcc; 
    #		0  excludes the mgiAcc # obj;
    #		-l excludes both the AccKey and mgiAcc objs.
    # OUTPUTS:     
    #   "boolean" -- true if all objects initialized successfully
    # ASSUMES:     
    # SIDE EFFECTS: 
    #   initializes module globals: accKey, mgiAcc, logicalDBs, mgiTypes
    # EXCEPTIONS: 
    # COMMENTS:  
    # MODIFICATIONS:
    # 12/15/97 rpp:
    # - replaced SQL class w/ mgdlib library module
    #--------------------------------------------------

    global accKey, mgiAcc, logicalDBs, mgiTypes

    returnFlag = 1
    try:
	if logicalDBs is None:
	    logicalDBs = LogicalDBLookUp( server, db, user, pwd )

	if mgiTypes is None:
	    mgiTypes = MGITypeLookUp( server, db, user, pwd )

	if includeAcc > -1 and accKey is None:
	    accKey = AccKey( server, db, user, pwd )

	if includeAcc > 0 and mgiAcc is None:
	    mgiAcc = MGIAccKey( server, db, user, pwd )

    except:
	print sys.exc_type, sys.exc_value, sys.exc_traceback
	# check in the same order as objects instantiated above	
	if logicalDBs is None:
	    sys.stderr.write( "Failed to initialize LogicalDBLookUp object"
			      + NL )
	elif mgiTypes is None:
	    sys.stderr.write( "Failed to initialize MGITypeLookUp object"
			      + NL )
	elif accKey is None:
	    sys.stderr.write( "Failed to initialize AccKey object" + NL )
	elif mgiAcc is None:
	    sys.stderr.write( "Failed to initialize MGIAccKey object" + NL )

	returnFlag = 0

    return returnFlag


# LOOK UP INTERFACE FUNCTIONS
#############################

def getLogicalDBKey ( name ):
    """ translate name to its key.
    """
    #--------------------------------------------------
    # INPUTS:     name as string
    # OUTPUTS:     int -- logical db Key of name
    # ASSUMES:     that the global object is instantiated (via init)
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or logicalDBs not initialized.
    #   KeyError via dictionary look-up failure
    # COMMENTS:  
    #--------------------------------------------------

    if type(name) is StringType:
	return logicalDBs [ name ]
    else:
	raise TypeError, "Arg. to getLogicalDBKey() must be a string"


def getLogicalDBName ( key ):
    """ translates key to its name value
    """
    #--------------------------------------------------
    # INPUTS:     key as int
    # OUTPUTS:     string -- logicalDB.name for key
    # ASSUMES:     that the global object is instantiated (via init)
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or logicalDBs not initialized.
    #   KeyError via dictionary look-up failure
    # COMMENTS:  
    #--------------------------------------------------

    if type(key) is IntType:
	return logicalDBs [ key ]
    else:
	raise TypeError, "Arg. getLogicalDBName() must be int"


def getLogicalDBObject ():
    """ returns reference to the underlying internal object.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     reference to the module's object; None if uninitialized.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    # Useful where interface functions prove incomplete/inadequate and 
    # more direct access to the underlying class provides required 
    # functionality.
    #--------------------------------------------------

    return logicalDBs


def hasLogicalDBName ( name ):
    """ returns boolean/flag, true if name exists in table.
    """
    #--------------------------------------------------
    # INPUTS:     name as string
    # OUTPUTS:     "boolean" -- does the look up table have the name
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    #   TypeError for invalid input data type or logicalDBs is uninitialized.
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    if type(name) is StringType:
	return logicalDBs.has_key ( name )
    else:
	raise TypeError, "Arg. to hasLogicalDBName() must be a string"


def hasLogicalDBKey ( key ):
    """ returns boolean/flag, true if key as int exists in table
    """
    #--------------------------------------------------
    # INPUTS:     key as int
    # OUTPUTS:     "boolean" -- does the look up table have the key
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or object uninitialized.
    # COMMENTS:  
    #--------------------------------------------------

    if type(key) is IntType:
	return logicalDBs.has_key ( key )
    else:
	raise TypeError, "Arg. to hasLogicalDBKey() must be int"


def getMGITypeObject ():
    """ returns a reference to the modules underlying object.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     reference to the module's object; None if object uninitialized.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    # Useful where interface functions prove incomplete/inadequate and 
    # more direct access to the underlying class provides required 
    # functionality.
    #--------------------------------------------------

    return mgiTypes


def getMGITypeKey ( name ):
    """ returns key corresponding to the name 
    """
    #--------------------------------------------------
    # INPUTS:     name as string
    # OUTPUTS:     int -- _MGIType_key value for name
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or object uninitialized.
    #   KeyError via dictionary look-up failure
    # COMMENTS:  
    #--------------------------------------------------

    if type(name) is StringType:
	return mgiTypes [ name ]
    else:
	raise TypeError, "Arg. to getMGITypeKey() must be a string"


def getMGITypeName ( key ):
    """ returns name corresponding to key
    """
    #--------------------------------------------------
    # INPUTS:     key as int
    # OUTPUTS:     string -- MGIType name for the _MGIType_key value, key.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or object uninitialized.
    #   KeyError via dictionary look-up failure
    # COMMENTS:  
    #--------------------------------------------------

    if type(key) is IntType:
	return mgiTypes [ key ]
    else:
	raise TypeError, "Arg. to getMGITypeName() must be int"


def hasMGITypeName ( name ):
    """ returns boolean/flag, true if name appears in table.
    """
    #--------------------------------------------------
    # INPUTS:     name as string
    # OUTPUTS:     "boolean" -- does the look up table have the name
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or object uninitialized.
    # COMMENTS:  
    #--------------------------------------------------

    if type(name) is StringType:
	return mgiTypes.has_key ( name )
    else:
	raise TypeError, "Arg. to hasMGITypeName() must be a string"


def hasMGITypeKey ( key ):
    """ returns "boolean" indicating if key exists in look-up table.
    """
    #--------------------------------------------------
    # INPUTS:     key as int
    # OUTPUTS:     "boolean" -- does the look up table have the key
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    #   TypeError for invalid input data type or object uninitialized.
    # COMMENTS:  
    #--------------------------------------------------

    if type(key) is IntType:
	return mgiTypes.has_key ( key )
    else:
	raise TypeError, "Arg. to hasMGITypeKey() must be int"


# ACCESSION KEY INTERFACE FUNCTIONS
###################################

def getAccKeyObject ():
    """ returns reference to the module's AccKey instance.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     reference to the module's AccKey instance-object
    # ASSUMES:     
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    # Useful where interface functions prove incomplete/inadequate and 
    # more direct access to the underlying class provides required 
    # functionality
    #--------------------------------------------------

    return accKey


def getInitialAccKey ():
    """ returns the _Accession_key value found in db when initialized.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- the value found in db when object initialized.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return accKey.getInitialKey()


def getLastAccKey ():
    """ returns the AccKey objects current (last used)
    _Accession_key value.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- the current accession key (last used).
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return accKey.getLastKey()


def getNextAccKey ():
    """ increments and returns the next available _Accession_key.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- the next available accession key value
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    #   causes class to increment its next available key.
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return accKey.getNextKey()


def stillValidAccKey ():
    """ returns a boolean indicating whether or not the DB
	has changed its max(_Accession_key) since object
	was initialized.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     "boolean" -- is db still consistent w/ the object.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return accKey.isStillValid()



# MGI: ACCESSION KEY INTERFACE FUNCTIONS
########################################

def getInitialMGIAcc ():
    """ returns the MGI:# last used in the DB.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- initial mgi accession key from db.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return mgiAcc.getInitialKey()


def getLastMGIAcc ():
    """ returns the last MGI:# used by the mgiAcc object.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- last mgi accession key generated/consummed.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return mgiAcc.getLastKey()


def getMGIAccObject ():
    """ returns reference to the module's mgiAcc object.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     reference to the module's MGIAccKey instance.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    # Useful where interface functions prove incomplete/inadequate and 
    # more direct access to the underlying class provides required 
    # functionality.
    #--------------------------------------------------

    return mgiAcc


def getNextMGIAcc ():
    """ increments and returns the next available MGI:#.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     int -- next available MGI accession number
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # causes class to increment to the next available mgi accession number.
    # EXCEPTIONS: 
    # COMMENTS:  
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! 
    # CURRENTLY THE CODE SUPPORTS ONE PREALLOCATED RANGE (IMAGE's 200000-700000)
    # THIS CODE MUST BE KEPT CURRENT WITH PREALLOCATED RANGES THAT DON'T
    # PHYSICALLY APPEAR IN THE DB!!!!!!
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! 
    #--------------------------------------------------

    return mgiAcc.getNextKey()


def reserveMGIAcc ():
    """ attempts to "reserve" the used range of MGI:# by updating
	the ACC_AccessionMax record for the "MGI" sequence; returns
	flag indicating if successful in updating db.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     "boolean" -- true if update of db succeeded.
    # ASSUMES:     that the global object is instantiated (via init)
    # ASSUMES:     
    # SIDE EFFECTS: 
    #   If the db's mgi accession key has not changed, the last generated value
    #   is written back to the ACC_AccessionMax table for the MGI: accession 
    #   sequence.
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    return mgiAcc.initialKey == mgiAcc.write()


# WARNING: this is a slow operation, because the query is slow.
def stillValidMGIAcc ():
    """ retrieves the last used MGI:# from the db.
    """
    #--------------------------------------------------
    # INPUTS:     none
    # OUTPUTS:     "boolean" -- true if mgi accession number in db still matches
    #   what was found on object instantiation.
    # ASSUMES:     that the global object is instantiated (via init)
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #   I've implemented the underlying query as a VERY safe check of
    #   the db's current mgi accession number, which is a slow query.
    #--------------------------------------------------

    return mgiAcc.isStillValid()


def mkAccession ( prefix, suffix, lDB, objKey, mgiType,
		  private=0, preferred=1 ):
    """
	creates a bcp entry as a LIST object
    """
    #------------------------------------------------------------------
    # INPUTS:     
    #   prefix : string -- lead part of accID
    #   suffix : int or string -- "numeric" part of accID
    #   lDB    : int or string -- _LogicalDB_key value or name
    #   objKey : int -- _Object_key value
    #   mgiType: int or string -- _MGIType_key value or name
    #   private : int optional; default 0
    #   prefered : int optional; default 1
    # OUTPUTS:     
    #   LIST of elements for an Accession record.
    # ASSUMES:     
    # -  That all EST accession records are NOT private and preferred.
    # -  That mgiType is global and intialized.
    # SIDE EFFECTS: 
    #   By calling for the next accession key (accKey.getNextKey()), 
    #   consumes that value (causes accKey to increment its internal
    #   variable.
    # EXCEPTIONS: 
    # COMMENTS:  
    #   For IDDS, the date columns in table should have column 
    #   defaults; and they should be set empty, so they get 
    #   initialized when the data is loaded.
    # MODIFICATIONS:
    # - 3/13/98 rpp:
    #   - fixed for any MGIType; added additional req'd parameter mgiType
    #   - exteneded to handle name to key conversions here.
    # - 3/12/98 rpp:
    #   - moved into this module for general use; revisions for this
    #     namespace;
    #   - added support for int suffix values;
    #   - added optional args for preferred and private
    # - 2/4/98 rpp:
    #   - MGI 1.0 revisions
    #------------------------------------------------------------------

    if type(suffix) is StringType:
	accID = prefix + suffix
    else:
	accID = prefix + str(suffix)

    if type (mgiType) is StringType:
	typeKey = getMGITypeKey ( mgiType )
    else:
	typeKey = mgiType

    if type (lDB) is StringType:
	lDBKey = getLogicalDBKey ( lDB )
    else:
	lDBKey = lDB

    return [ getNextAccKey(),	    # _Accession_key
	     accID,			# accID
	     prefix,		    # prefixPart
	     suffix,		    # numericPart
	     lDBKey,		    # _LogicalDB_key
	     objKey,		    # _Object_key
	     typeKey,		    # _MGIType_key
	     private,		    # private
	     preferred,		    # preferred
	     None,			# cr-date
	     None,			# mod-date
	     None			# rel-date
	     ]




#**********************************************************************
# END PUBLIC MODULE SERVICES:
#**********************************************************************

#**********************************************************************
# BEGIN "PRIVATE" MODULE CODE:
#**********************************************************************

class DBTranslationTable:
    """ 
    Is a generic look-up/translation table mechanism for simple look ups.
    DATA MEMBERS:
    nameKeyDict : ("private") dictionary mapping names to db key values
    keyNameDict : ("private") dictionary mapping keys to names
    server : string -- connection parameter
    database : string -- connection parameter
    user : string -- connection parameter
    password : string -- connection parameter

    METHODS:
    __init__ (): called to initialize common class members
	#must be defined in the sub-class which knows its query
	#and how to contruct the dictionary implementation of the look up table.

    __str__ () : conversion utility for being able to print the class' data.
    __call__( key as string OR as int) :
	function call style -- return None if the requested key is not found;
	user must check return type.
    __getitem__ ( key as string OR as int) :
	dictionary-access style.
    __len__ () : returns # items in table(s)
    has_key ( key as string OR int) :
		returns true=1/false=0 on key exists or not; completes
		dictionary-style.

    USEAGE:
    Super-class; derived class must define the correct sql query.

    NOTES:
    While data should not differ from instance to instance and only one
    instance is expected to exist, the data is stored as instance variables
    instead of class globals.  Multiple instantiation is unnecessary.
    """

    def __init__ ( self, server, database, user, pwd ):
	""" constructor
	"""
	#--------------------------------------------------
	# INPUTS:     
	#  server, database, user & pwd as string -- connection params.
	# OUTPUTS:     none
	# ASSUMES:     
	# SIDE EFFECTS: 
	#  initializes class data members
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	self.server = server
	self.database = database
	self.user = user
	self.password = pwd
	self.nameKeyDict = {}
	self.keyNameDict = {}


    def __str__ ( self ):
	""" printable representation of the data as dictionary. """
	#------------------------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     string -- representation of the two look up dictionaries.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------

	return str(self.nameKeyDict) + NL + str(self.keyNameDict)


    def __call__ (self, key ):
	""" function-call style look up;
	return the corresponding "translation" of key.
	"""
	#--------------------------------------------------
	# INPUTS:     key as int OR string.
	# OUTPUTS:     
	#   returns the translation of input (key-to-name or name-to-key)
	#    case-insensitive, function-call style look up.
	#    Unlike dictionaries, an erroneous request will NOT cause a
	#    runtime exception, but returns None.
	# ASSUMES:     input is either int or string
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	if type(key) is IntType:
	    if self.keyNameDict.has_key (key):
		return self.keyNameDict [ key ]
	    else:
		return None
	else:
	    key = string.upper(key)
	    if self.nameKeyDict.has_key (key):
		return self.nameKeyDict [ string.upper(key) ]
	    else:
		return None


    def __getitem__ ( self, key ):
	""" dictionary-style look-up; 
	return the corresponding "translation" of key.
	"""
	#--------------------------------------------------
	# INPUTS:     key as INT or STRING
	# OUTPUTS:     
	#    returns string for int or int for string
	# ASSUMES:     input is either int or string
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	#   raises dictionary key errors
	# COMMENTS:  
	#--------------------------------------------------

	if type(key) is IntType:
	    return self.keyNameDict [ key ]
	else:
	    return self.nameKeyDict [ string.upper(key) ]


    def __len__ ( self ):
	""" returns number of entries in the look up table. """
	#------------------------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- number of items in dictionary
	# ASSUMES:     
	#   That both the id and the name are unique.
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	return len ( self.keyNameDict )


    def has_key ( self, key ):
	""" returns boolean indicating if look-up has the key. """
	#--------------------------------------------------
	# INPUTS:     key as INT or STRING
	# OUTPUTS:     0 or 1 whether key exists in table
	# ASSUMES:     input is either int or string
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  completes the dictionary-style look-up.
	#--------------------------------------------------

	if type(key) is IntType:
	    return self.keyNameDict.has_key ( key )
	else:
	    return self.nameKeyDict.has_key (string.upper(key))



class LogicalDBLookUp (DBTranslationTable):
    """ Provides a case-insensitive look-up mechanism for Logical DB's where
	one needs to keep the information available for repeated referencing.

    DATA MEMBERS:
    nameKeyDict : (inherited & "private") dictionary mapping names to db 
		    key values.
    keyNameDict : (inherited & "private") dictionary mapping keys to
		    name values.
    server : (inherited) string -- connection parameter
    database : (inherited) string -- connection parameter
    user : (inherited) string -- connection parameter
    password : (inherited) string -- connection parameter


    METHODS:
    __init__ (server, database, user, password) : all args as string.
	Runs the required query and saves results in a pair of dictionary data
	structs.

    (inherited) __str__ () : conversion utility to print the class' data.
    (inherited) __call__( logicalDBName as string OR logicalDB_key as INT) :
	function call style; translates between key-name and name-key.
    (inherited) __getitem__ ( logicalDBName as string OR key as INT) :
	dictionary-access style.
    (inherited) __len__ () : returns # items in "table"
    (inherited) has_key ( logicalDBName as string OR key as int ):
	returns 1/0 on key exists; completes dictionary-style.

    USEAGE:
    Class can be used to look up internal db keys for supplied logical db names
    using either a function call or dictionary style.

    NOTES:

    MODIFICATIONS:
    12/15/97 rpp: replaced sql module with mgdlib library
    11/20/97 rpp: migrated DBLookUpTable to DBTranslationTable.
    11/18/97 rpp: abstracted similarities to DBLookUpTable.
    """

    def __init__ ( self, server, database, user, pwd ):
	""" fetch rows from db into the tables.
	"""
	#--------------------------------------------------
	# INPUTS:     server, database, user, pwd all as string
	# OUTPUTS:     none
	# ASSUMES:     
	# SIDE EFFECTS: initializes the instance data members
	# EXCEPTIONS: an empty result set is considered fatal since
	#    this should be a standard look up table on the db.
	# COMMENTS:  
	#--------------------------------------------------

	DBTranslationTable.__init__ ( self, server, database, user, pwd )

	qry = "select _LogicalDB_key, name from ACC_LogicalDB" 
	qResults = sql ( qry, server, database, user, pwd )
	if len(qResults) == 0:
	    sys.stderr.write (
		"Failed to get LogicalDB from ACC_LogicalDB." + NL )
	    sys.exit(1)
	else:
	    for row in qResults:
		self.nameKeyDict [string.upper(row["name"]) ] = \
				 row["_LogicalDB_key"]
		self.keyNameDict [ row["_LogicalDB_key"] ] = row ["name"]



class MGITypeLookUp (DBTranslationTable):
    """ Provides a look-up mechanism for MGIType's.

    DATA MEMBERS: 
    nameKeyDict : (inherited & "private")
		dictionary mapping names to db key values.
    keyNameDict : (inherited & "private")
		dictionary mapping keys to name values.
    server : (inherited) string -- connection parameter
    database : (inherited) string -- connection parameter
    user : (inherited) string -- connection parameter
    password : (inherited) string -- connection parameter


    METHODS:
    __init__ (server, database, user, password) : all args as string.
	Runs the required query and saves results in a pair of dictionary data
	structs.

    (inherited) __str__ () : conversion utility for being able to print
			    the class' data.
    (inherited) __call__( logicalDBName as string OR logicalDB_key as INT) :
	function call style; translates between key-name and name-key.
    (inherited) __getitem__ ( logicalDBName as string OR key as INT) :
	dictionary-access style.
    (inherited) __len__ () : returns # items in "table"
    (inherited) has_key ( logicalDBName as string OR key as int ):
	returns 1/0 on key exists; completes dictionary-style.

    USEAGE:
    Class can be used to look up internal db keys for supplied MGI_Type names
    using either a function call or dictionary style.

    NOTES:

    MODIFICATIONS:
    12/15/97 rpp: replaced sql module with mgdlib library
    11/18/97 rpp: abstracted similarities to DBTranslationTable
    """

    def __init__ ( self, server, database, user, pwd ):
	""" fetch rows into the tables."""
	#--------------------------------------------------
	# INPUTS:     server, database, user, pwd all as string
	# OUTPUTS:     none
	# ASSUMES:     
	# SIDE EFFECTS: initializes the instance data members
	# EXCEPTIONS: an empty result set is considered fatal since
	#    this should be a standard look up table on the db.
	# COMMENTS:  
	#--------------------------------------------------

	DBTranslationTable.__init__ ( self, server, database, user, pwd )

	qry = "select _MGIType_key, name from ACC_MGIType" 
	qResults = sql ( qry, server, database, user, pwd )

	if len(qResults) == 0:
	    sys.stderr.write ( "Failed to get MGIType keys from ACC_MGIType."
			       + NL )
	    sys.exit(1)
	else:
	    for row in qResults:
		self.nameKeyDict[ string.upper(row["name"]) ] = \
				  row["_MGIType_key"]
		self.keyNameDict[ row["_MGIType_key"] ] = row ["name"]




class Sequencible:
    """ 
    Abstract Class used by AccKey & MGIAccKey classes to provide core methods.

    DATA MEMBERS:
    all are instantiated by the sub-class, but:
    at minimum, lastUsed & initialKey are EXPECTED to exist!
    lastUsed : int -- last used accession number
    initialKey : int -- initial value when loaded from db

    METHODS:
    __init__(): constructor.
    __str__() : returns a string representation of initialKey & lastUsed 
    getInitialKey() : returns self.initialKey (int).
    getLastKey() : returns self.lastUsed (int).
    getNextKey() : returns incremented value of self.lastUsed (int).

    USEAGE:
    DO NOT DIRECTLY INSTANTIATE.

    NOTES:
    The class uses instance variables (in place of class variables), however
    only one instance of each subclass is expected to be instantiated.

    MODIFICATIONS:
    2/18/98 rpp:
    - extended getNextKey() to support steps other than 1.
    12/3/97 rpp:
    - completed conversion from class global data members (C++ class statics).
    11/19/97 rpp:
    -   removed __call__() function-style interface (function overloading)
    -   added isStillValid () to determine if db still matches initialKey
    11/14/97 rpp:
    -    modified __str__() to include displaying the initial key.
    """

    def __init__ ( self, server, database, user, password ):
	"""
	Default constructor: loads generic instance variables.
	"""
	#--------------------------------------------------
	# INPUTS:     
	#  server, database, user & password as strings -- connection
	#     parameters.
	# OUTPUTS:     none
	# NOTE: Call explicitly from sub-class's constructor.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	# the key and derived sequence is only valid for one server
	self.server = server
	self.database = database
	self.user = user
	self.password = password
	self.initialKey = self.lastUsed = self.getCurrKeyFromDB()


    def __str__ ( self ):
	""" string representation of object's data. """
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     string representation of object's primary data members.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	return "Initial Key = %u; Curr. Key = %u" % (
	    self.initialKey, self.lastUsed
	    )


    def getInitialKey ( self ):
	""" returns the key value found when object was loaded. """
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     initialKey value : int
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	return self.initialKey

    def getLastKey ( self ):
	""" returns the last key value used by object. """
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     self.lastUsed : int -- last value used as a key
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	return self.lastUsed

    def getNextKey ( self, step=1 ):
	""" 
	default implementation that increments the sub-Class object's 
	self.lastUsed and returns the new value.
	"""
	#--------------------------------------------------
	# INPUTS:     step : int OPTIONAL, for non-1 increments
	# OUTPUTS:     self.lastUsed int -- updated last used key.
	# ASSUMES:     
	# SIDE EFFECTS: 
	#   increments self.lastUsed data member.
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	self.lastUsed = self.lastUsed + step
	return self.lastUsed

    def isStillValid ( self ):
	"""
	Checks current state of db to determine if sequence basis has been
	changed.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     boolean/int true if db value still matched self.initialKey
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	return self.initialKey == self.getCurrKeyFromDB()



class AccKey ( Sequencible ):
    """
       Class will fetch the max used accession key and provides a
       controlled mechanism for returning next available numbers;
       it assumes no other user is creating accession records in the
       database or in bcp files for later loading.  


    DATA MEMBERS:
    lastUsed : int (inherited) -- last accession key used.
    initialKey : int (inherited) -- value when 1st class object instantiated.
    // following all remember the db connection parameter for reconnecting
    server : string (inherited)
    database : string (inherited)
    user : string (inherited)
    password : string (inherited)

    DEPENDS ON: class Sequencible

    METHODS:
    __init__ ( server, database, user, password ) all as string
    (inherited) __str__ () : printable representations
    (inherited) __call__() : function-call style to get next available 
	accession key.
    getCurrKeyFromDB() : retrieves the current value directly from the db; used
	to initialize initialKey and subsequently determine if any inserts to
	ACC_Accession have occurred.
    (inherited) getNextKey () : increments self.lastUsed, returns new val.
    (inherited) getInitialKey () : returns key originally found in the db
    (inherited) getLastKey () : returns current value of lastUsed

    USEAGE:
    # instantiate (one or more instances) of class
    accKey = AccKey ( server, database, user, password )
    # get next _Accession_key
    # do some processing which needs next available _Accession_key
    for ...:
	...
	accession_key = accKey()
	...
    # when done, check if db has changed since started
    if not accKey.isStillValid():
	print "Someone else has updated the ACC_Accession table"
	sys.exit(1)

    NOTES:

    ASSUMES: 
	That only one object will be instantiated.

    POSSIBLE IMPROVEMENTS:

    MODIFICATIONS:
    12/15/97 rpp: replaced sql module with mgdlib library
    12/3/97 rpp:
    -   completed conversion from class global data members (C++ class statics).
    11/20/97 rpp:
    -   revised to eliminate class globals for object vars
    11/14/97 rpp:
    -    extracted common features to super class Sequencible
    -    renamed nextKey() to getLastKey() (nextKey was bad choice of name);
    -    added getInitialKey() to chech key originally found in the db.
    -   added getNextKey() as alternate syntax to calling the class object.

   10/22/98: 
   -    extended to be able to recheck the db current value.  
    """

    def __init__ ( self, server, database, user, pwd ):
	""" constructor
	"""
	#--------------------------------------------------
	# INPUTS:     
	#   server, database, user, pwd all as string -- connection args.
	# OUTPUTS:     none
	# ASSUMES:     Only one object instantiated.
	# SIDE EFFECTS: initializes object's data members.
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	Sequencible.__init__( self, server, database, user, pwd )


    def getCurrKeyFromDB ( self ):
	""" fetches the current max(_Accession_key) from the db.
	    Because it goes back to the db, can be used to verify that db has
	     not changed while we've been using this sequence.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- highest used Accession Key in db.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	qry = """select lastUsed = isnull (max(_Accession_key), 0)
	      from acc_accession
	      """
	qResults = sql ( qry,
			 self.server, self.database, self.user, self.password )

	return qResults[0]["lastUsed"]




class MGIAccKey ( Sequencible ):
    """Class will fetch the max used MGI accession key and provides a
       controlled mechanism for allocating next available mgi accession
       number; it assumes no other user is creating accession records.

    DATA MEMBERS:
    lastUsed : int
    initialKey : int
    dbUpdated : "boolean" flag when update db to values used.
    // following all remember the db connection parameter for reconnecting
    server : string
    database : string
    user : string
    password : string

    METHODS:
    __init__ ( server, database, user, password ) all as string
    (inherited) __str__ () : printable representations
    (inherited) __call__() : function-call style to get next available
			    accession key
    getCurrKeyFromDB() : retrieves the current value directly from the db; used
	to initialize initialKey and subsequently determine if any inserts to
	ACC_Accession have occurred.
    getNextKey () : returns int -- implements method style useage; increments
	the self.lastUsed and returns new value.
    (inherited) getInitialKey () : returns key originally found in the db
    (inherited) getLastKey () : returns current value of lastUsed
    write () : returns the db ACC_AccessionMax.maxNumericPart for MGI:# after 
	attempting to update the db's ACC_AccessionMax table's 'MGI:' record.

    USEAGE:
    # instantiate (one or more instances) of each class
    accKey = AccKey ( server, database, user, password )
    mgiKey = MGIAccKey ( server, database, user, password )
    # do some processing which needs next available _Accession_key and MGI:#
    for ...:
	...
	accession_key = accKey()
	mgiAccession = mgiKey()
	...
    # when done, check if db has changed since started
    isMGIkeySame = mgiKey.getInitialKey() == mgiKey.getCurrKeyFromDB()
    if not isMGIkeySame:
	print 'Someone else has added an MGI Accession number.'
	sys.exit(1)
    isAccKeySame = accKey.getInitialKey() == accKey.getCurrKeyFromDB()
    if not isAccKeySame:
	print ( 'Someone else has added an accession number to the'
		+ ' ACC_Accession table' )
	sys.exit(1)

    NOTES:
    Since the query gets the max. from ACC_Accession and ACC_AccessionMax,
    it will handle preallocated ranges IFF they record the preallocation
    in ACC_AccessionMax.

    MODIFICATIONS:
    2/18/98 rpp: 
    -  added generic PrimaryKeySequence class, for generating pk for 
       int-keyed tables.
    -  renamed Accessionable to Sequencible
    -  revised generic DBLookUp to use column names in returned dictionary
       to determine dictionary substripts and which is int and which is
       string.
    12/15/97 rpp: replaced sql module with mgdlib library
    12/3/97 rpp:
    -   completed conversion from class globals (C++ class statics).
    -   added holdlock to write() method's transaction query.
    12/2/97 rpp:
    -   Added dbUpdated flag to track success/fail of write method.
    11/14/97 rpp:
    -    Revised to derive from Sequencible class.
    10/22/97 rpp:
    -    Added getCurrKeyFromDB() method to allow requery of db value.
    -    Added a write() method to allow object to update the db ACC_AccessionMax
	maxNumericPart for ID's that were used.

    """

    def __init__ ( self, server, database, user, pwd ):
	""" constructor
	"""
	#--------------------------------------------------
	# INPUTS:     
	#    server, database, user, pwd as string -- connection args.
	# OUTPUTS:     none
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------

	Sequencible.__init__( self, server, database, user, pwd )
	self.dbUpdated = None				# not used yet


    def getCurrKeyFromDB ( self ):
	""" fetches the current last MGI# from the DB via an SQL query.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- last used MGI accession number in db.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	# Implements a "safe" check for last used number by taking
	# the max of either what's in ACC_Accession as MGI:#'s and
	# what's in the ACC_AccessionMax for MGI: sequence.
	#--------------------------------------------------

	qry = """select lastUsed = isnull (max(numericPart), 0)
	    from acc_accession where prefixPart = 'MGI:'
	    UNION ALL
	    select maxNumericPart 
	    from acc_accessionMax where prefixPart = 'MGI:'
	    """

	qResults = sql ( qry,
			 self.server, self.database, self.user, self.password )

	if len (qResults) == 0:
	    currKey = 0
	else:
	    currKey = qResults[0]["lastUsed"]
	    if len(qResults) == 2 and qResults[1]["lastUsed"] > currKey:
		currKey = qResults[1]["lastUsed"]

	return currKey



    def getNextKey ( self ):
	""" Increments next key and returns it.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- next available mgi: accession number
	# ASSUMES:     
	# SIDE EFFECTS: 
	#   increments self.lastUsed before returning new value.
	# EXCEPTIONS: 
	# COMMENTS:  
	#    Overrides Super-class default method in order to block out 
	#    preallocated range of accession numbers.
	#--------------------------------------------------

	self.dbUpdated = 0
	# 200000 - 700000 reserved for Image and est data
	if 200000 <= self.lastUsed <= 700000:
	    self.lastUsed = 700001
	else:
	    self.lastUsed = self.lastUsed + 1
	return self.lastUsed



    def write ( self ):
	""" performs a safe update to the DB's ACC_AccessionMax table's
	    MGI accession sequence.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- MGI:# when update attempted; if returned value
	#   matches initial value update succeeded; otherwise it failed.
	# ASSUMES:     
	# SIDE EFFECTS: 
	#    The SQL update statement will only update the db IF the initial
	#    value in maxNumericPart matches what was found when class 1st
	#    instantiated.
	# EXCEPTIONS: 
	#   Any problems with the server, connection or SQL syntax will
	#   cause sybaselib to raise an exception; unexpected; not handled.
	# COMMENTS:  
	#   If the query returns the same initial value queried from the DB
	#    then it succeeded; otherwise it failed.
	# MODIFICATIONS:
	# 12/17/97 rpp: correction for mgdlib.sql nested list results
	# 12/15/97 rpp: replaced sql module with mgdlib library
	# 12/15/97 rpp: 
	# - fixed typo (initalKey)
	# - replaced local var initalKey with expression in one place used.
	# 12-3/97 rpp:
	#   Added holdlock to select query to insure the @initKey assignment
	#   is still valid after the update statement, preventing another
	#   process from inserting a new value between the test and the update.
	#--------------------------------------------------

	lastUsed = str (self.lastUsed)

	qry = [
	    """declare @initKey int
	       begin transaction""",
	    "select @initKey = (select maxNumericPart from ACC_AccessionMax "
		+ "holdlock where prefixPart = 'MGI:' )",

	    "update ACC_AccessionMax set maxNumericPart = "
		+ lastUsed
		+ " where prefixPart = 'MGI:' and maxNumericPart = "
		+ str (self.initialKey),

	    "commit transaction",
	    "select initKey=@initKey",
	    ]

	
	qResults = sql ( qry, self.server, self.database,
			 self.user, self.password )[-1]      # last has result set.

	if len(qResults) == 0:
	    self.dbUpdated = 0
	    return -1
	else:
	    keyWas = qResults[0]["initKey"]
	    if keyWas == self.initialKey:
		self.dbUpdated = 1
	    else:
		self.dbUpdated = 0
	    return keyWas
		   


re_accNumpart = regex.compile ("[0-9]+$")		    # for accSplit()

def accSplit ( s ):
    """
       splits a string into a prefix and numeric part,
       returning it as a tuple of strings
       this version returns strings, possibly empty instead of None
    """
    #--------------------------------------------------
    # INPUTS:     s : string -- accession key to be split
    # OUTPUTS:     tuple containing the prefix and suffix components
    # ASSUMES:     
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    splitAt = re_accNumpart.search(s)
    if splitAt == -1:					# not found
	splitAt = len(s)+1				    # so all prefix
    return (s[:splitAt], s[splitAt:])



def sql (qry, server=None, database=None, user=None, password=None ):
    """provides a login safe way of running query using db
    """
    #--------------------------------------------------
    # INPUTS:     
    #   qry : string or list of strings, pass-thru to db.sql()
    #   user : (optional) string
    #   password : (optional) string
    #   database : (optional) string
    #   server : (optional) string
    # OUTPUTS:     
    #   returns results from db.sql() -- 
    #       list of dictionary or list of lists of dictionaries
    # ASSUMES:     
    #   Login params should be either all None or all supplied.
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #   Parameter ordering (most general to most specific) is more natural
    #   to me and consistent with existing code in EST scripts for which this
    #   wrapper function was developed.
    #--------------------------------------------------

    if user is not None:
	oldLogin = db.set_sqlLogin (user, password, server, database)
    else:
	oldLogin = None


    try:
	qResults = db.sql (qry, 'auto')
    except:
	if oldLogin:
	    # restore to original values
	    apply ( db.set_sqlLogin, oldLogin )
	# pass the exception on up
	raise sys.exc_type, sys.exc_value, sys.exc_traceback
    else:
	if oldLogin:
	    # restore to original values
	    apply ( db.set_sqlLogin, oldLogin )

    return qResults



#**********************************************************************
# BEGIN "PUBLIC" CLASS CODE:
#**********************************************************************


class DBLookUp (DBTranslationTable):
    """ Provides a generic way to load translation tables from the db;
	these provide case insensitive, bi-directional translations.

    DATA MEMBERS: all inherited from base class

    METHODS: 
	__init__(self, qryStr, serverStr, dbStr, userStr, pwdStr)
	rest inherited from base class

    USEAGE:
	vectLookup = DBLookUp (
		'select _Vector_key, vector from PRB_Vector_Types',
		<server>, <database>, <user>, <pwd> )
	notSpecVector = vectLookup["Not Specified"]
    NOTES:

    ASSUMES:
    - That there is a int key and a string representation between
      which there is a 1:1 correspondence w/o duplicates.

    MODIFICATIONS:
    9/23/1999 rpp:
    -  added logic to allow qry arg to be more complex (list)
    2/18/98 rpp:
    -  modified __init__() to use the returned dictionary to discover the
       int and string col names.
    """

    def __init__( self, qry, server, database, user, pwd):
	""" initialize the look-up structures 
	"""
	#------------------------------------------------------------------
	# INPUTS:     
	#   qry : string (form: 'select <intKey>, <strVal> from tbl ...'
	#	 OR list of strings in which last query returns results.
	#   server, database, user, pwd all as string -- connection args.
	# OUTPUTS:     none
	# ASSUMES:     
	#   That the qry argument specifies two columns, one interger
	#   key value, another the string value column.
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	#   Will trigger sql exceptions for invalid query string.
	# COMMENTS:  
	#------------------------------------------------------------------

	DBTranslationTable.__init__ ( self, server, database, user, pwd )

	qResults = sql ( qry, server, database, user, pwd )
	if len(qResults) == 0:
	    sys.stderr.write (
		"Failed to get results for:" + qry + "." + NL )
	else:
	    # was this a complex query; expect results at end
	    if type (qResults[0]) is ListType and len (qResults) > 1:
		qResults = qResults[-1]
	    colNames = qResults[0].keys()
	    if type (qResults[0][colNames[0]]) is IntType:
		intCol = colNames[0]
		strCol = colNames[1]
	    else:
		strCol = colNames[0]
		intCol = colNames[1]

	    for row in qResults:
		self.nameKeyDict [string.upper(row[strCol]) ] = \
				 row[intCol]
		self.keyNameDict [ row[intCol] ] = row [strCol]




class PrimaryKeySequence (Sequencible):
    """ Generic class for providing sequential IDs based on an SQL query
	that returns a single value.

    DATA MEMBERS: 
	keyQuery : string -- query used to fetch the current key from db
	all others inherited from base class.

    METHODS:
	__init__(qry, server, datbase, user, pwd) all as string
	getCurrKeyFromDB () : returns the value from the db.

    USEAGE:
	strainKey = PrimaryKeySequence(
	    "select max(_Strain_key) from PRB_Strain",
	    "MGD_PUBLIC", "mgd", "mgd_public", "mgdpub" )
	newStrainKey = strainKey.getNextKey()

    NOTES:
    - Unlike the accession objects above, instances of this class don't 
      protect the user from shooting themselves in the foot by mis-use
      -- i.e. instantiating multiple instances for the same table!

    ASSUMES:
    - Supplied query will return only a single row, single columned result set.
    - That the sequence begins immediately after the returned value, with
      default increases by 1.
    - That the user does not instantiate multiple instances for the same 
      sequence/table (unless any keys used have been written back to the db),
      thus causing duplicated keys.

    MODIFICATIONS:

    """

    def __init__ (self, qry, srvr, db, user, pwd):
	""" constructor -- fetches db curr key via supplied query"""
	#--------------------------------------------------
	# INPUTS:     
	#   qry : string -- SQL query to get current key from db.
	#   server, database, user, pwd all as string -- connection args.
	# OUTPUTS:     none
	# ASSUMES:     Only one object instantiated.
	# SIDE EFFECTS: initializes object's data members.
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------
	self.keyQuery = qry
	Sequencible.__init__(self, srvr, db, user, pwd)


    def getCurrKeyFromDB (self):
	""" fetches the current key from the db.  Because it goes back
	    to the db, can be used to verify that db has not
	    changed while we've been using this sequence.
	"""
	#--------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- return value of the query
	# ASSUMES:     that the sql query will return a single row
	#	   dictionary w/ just one value.
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# - if the query fails, exception will be raised via sql()
	# - if the query returns 0 rows, a subscript exception will
	#   occur.
	# COMMENTS:  
	#  Will use the returned dictionaries keys() list
	#  to get the single value expected
	#--------------------------------------------------
	
	# query should return a list of 1 dictionary w/ 1 entry:
	# save just the row of interest
	qResult = sql ( self.keyQuery, self.server, self.database,
			 self.user, self.password ) [0]
	
	# now extract whatever column was returned from the row/tuple
	return qResult [ qResult.keys()[0] ]




#*******************************************************
#*  TEST DRIVER
#*******************************************************

if __name__ == "__main__":

    # for Accessionable objects -- default connection args.:
    server = "MGD_DEV"
    db = "mgd"
    user = "mgd_public"
    pwd = "mgdpub"

    argc = len(sys.argv)
    if argc > 1:
	server = sys.argv[1]
	if argc > 2:
	    database = sys.argv[2]
	    if argc > 3:
		user = sys.argv[3]
		if argc > 4:
		    pwd = sys.argv[4]			# assume explicit
		    if os.path.isfile(pwd):		    # is pwdFileName
			fd = open(pwd)
			pwd = fd.readline()[:-1]	    # except \n
			fd.close()

    print "Server: %s, Database: %s, user: %s" % (server, db, user)
    print "initializing all objects (MGIAccKey takes several minutes)..."
    if not init (server, db, user, pwd):
	print "failed to initialize"
	sys.exit(1)

    # these are "alias" for these objects to test the object-reference access
    ldbs = getLogicalDBObject()
    mgitypes = getMGITypeObject()
    acckey = getAccKeyObject()
    mgiacc = getMGIAccObject()

    print "testing Translation tables"
    
    print "LogicalDBs: # entries: %u; dictionary:\n %s" % (
	len(ldbs), str(ldbs))
    print "MGI _LogicalDB_key = %u" % ldbs ["MGI"]
    print "getLogicalDBKey('I.M.A.G.E.') = %u" % getLogicalDBKey('I.M.A.G.E.')
    print "getLogicalDBName(1) = %s" % getLogicalDBName(1)
    print "hasLogicalDBKey(1) = %u" % hasLogicalDBKey(1)
    print "hasLogicalDBKey(0) = %u" % hasLogicalDBKey(0)
    print "hasLogicalDBName('atcc') = %u" % hasLogicalDBName ('atcc')
    print "hasLogicalDBName('junk') = %u" % hasLogicalDBName ('junk')

    print ""
    print "MGITypes: # entries: %u; dictionary:\n %s" % (
	len(mgitypes), str(mgitypes))
    print "Segment _MGIType_key = %u" % mgitypes ["Segment"]
    print "getMGITypeKey('Segment') = %u" % getMGITypeKey('Segment')
    print "getMGITypeName(1) = %s" % getMGITypeName(1)
    print "hasMGITypeKey (1) = %u" % hasMGITypeKey (1)
    print "hasMGITypeKey (0) = %u" % hasMGITypeKey (0)
    print "hasMGITypeName ('experiment') = %u" % hasMGITypeName ('experiment')
    print "hasMGITypeName ('junk') = %u" % hasMGITypeName ('junk')


    print NL + "testing AccKey & interface functions"

    print "Accession Key: %s" % str(acckey)
    print "Accession Key getInitialKey()", acckey.getInitialKey()
    print "getInitialAccKey()", getInitialAccKey()

    print "\nTest using accession numbers via method style:"
    for i in range (3):
	print "next accession key:", acckey.getNextKey()
	print "Accession Key: %s" % str(acckey)
	print ""

    print "\nTest using interface functions:"
    for i in range (3):
	print "getNextAccKey()", getNextAccKey()
	print "getInitialAccKey() %u getLastAccKey() %u" % (
	    getInitialAccKey(), getLastAccKey() )
	print ""

	
    print ("Accession Key: method getCurrKeyFromDB() = %u"
	   % acckey.getCurrKeyFromDB() )
    print "Accession Key: method getLastKey() %u" % acckey.getLastKey()
    print "stillValidAccKey()", stillValidAccKey()


    print NL + "testing MGIAccKey and interface functions:"

    print "MGI Accession #: %s\n" % str(mgiacc)
    print "MGI Accession Key getInitialKey()", mgiacc.getInitialKey()
    print "getInitialMGIAccKey()", getInitialMGIAcc()


    print "\nTest using accession numbers via method style:"
    for i in range (3):
	print "next mgi accession #:", mgiacc.getNextKey()
	print "MGI Accession #: %s" % str(mgiacc)
	print ""

    print "\nTest using interface functions:"
    for i in range (3):
	print "getNextMGIAcc()", getNextMGIAcc()
	print "getInitialMGIAcc() %u getLastMGIAcc() %u" % (
	    getInitialMGIAcc(), getLastMGIAcc() )
	print ""

    # SLOW:
    # print ( "\nMGI Accession #: getCurrKeyFromDB() = %u"
    #    % mgiacc.getCurrKeyFromDB()
    print NL + "MGI Accession # getLastKey() %u" % mgiacc.getLastKey()
    print "stillValidMGIAcc()", stillValidMGIAcc()
