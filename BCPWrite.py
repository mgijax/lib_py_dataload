#! /usr/local/bin/python

############################################################################
#
#  Author:    R. Palazola
#  Date:    11/97
#  Purpose: 
#    Provide a generic facility for writing output in text-delimited
#    format (text bcp files).
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

"""
    BCP-Write module.
    R. Palazola
    11/18/97
    Copyright 1997, The Jackson Laboratory

    Module to facilitate generating bcp files.

INTRODUCTION:
    Much of our migration used python code to control the format
    (column order and column and row separators).  When unusual things
    like embedded tabs & newlines cause the bcp operation to fail, we
    have to go back and recode the python and the shell scripts that
    load the bcp.

    By encapsulating the bcp writing within this class we make it easier
    to change the delimiters for an entire program in just one place.

    Sometimes a straight forward sql query can produce the raw data to
    generate the bcp output.  This module was written to accept the 
    standard sql result set (list of dictionaries) for direct output; it
    was then extended to handle list of lists as well.  

    The list of lists is easier when working with text-file inputs; the 
    list of dictionaries is easier with sql result sets.

    The class constructor takes a file (name or handle), a list of
    dictionaries (optional), and a list defining the column ordering 
    (optional).

    NOTE: the output data is not required to create the class, but if 
    present, it will cause the class to output the data as part of 
    initializing itself.

    Actually the output data can be any list of subscriptable objects:
    for example a list of lists (subscripts would be integers); a list
    of dictionaries (subscripts & cols would be the dictionary keys);
    or class or list of class objects that implement subscript-methods.

    Since dictionaries are unordered sets and since we may need to
    provide place holder columns, a colList argument, which gets assigned
    to the class data-member 'cols', provides the mechanism for controlling
    the column selection, ordering and dummy/place-holder values.  Any
    output column key specification not found in the input data structure
    is considered a 'literal' to be output in that column position.

    The BCPWrite class allows the client to modify the column and row
    separator tokens.  

USING THE BCPWrite MODULE:
    The class constructor takes three arguments:
    1. A filename or FILE object
    2. (optional) a set of data to be written out
    3. (optional) a list of indices or dictionary keys used to control
       ordering of output. (For a List of Lists dataset, the default
       ordering is 0..N for the inner List; for List of Dictionaries,
       a list of ordered keys is needed as the default order is arbitrary.)

Include either:
    from BCPWrite import BCPWrite		  # I'll use this form
or
    import BCPWrite

depending on how you want to address the class ( BCPWrite() or 
BCPWrite.BCPWrite() ).


EXAMPLES:
    from mgdlib import sql
    from BCPWrite import BCPWrite
    BCPWrite ( 'out.bcp', 
	       sql('select c1, c2, c3 from mytable', 'auto'), 
	       ['c1', 'c2', 'c3' ] )

The above code gets data from a table and writes it to 'out.bcp' using 
the default column and row delimitors ('|' and '\n' respectively).  The 
output file is created, written to and closed; the columns are not
reordered, but they could be by reordering the third, colList arg. 

The next code fragment generates a bcp file from an array:

    BCPWrite ( 'lookup.bcp', 
	       [ ['a', 'b', 'c'],['d', 'e', 'f'] ],
	       [1,2,3] )

The results should look like:
a|b|c
d|e|f

Passing None as the output data argument, causes the class to initialize 
itself without outputting any data.  The instance's write() method can be 
invoked later with the data, possibly partial subsets of the entire output 
data.

    bcp = BCPWrite ( 'output.bcp', None, someListOfOutputColumns )
    rows = sql ('....', 'auto')
    for row in rows:
	# do something to the row columns, 
	# e.g. normalize names w/ keys
    bcp.write ( rows )

This form is useful for iterating over result sets.  

This kind of access was needed for migrating BIB_Refs table where the 
genbankID column had to be unpacked and normalized for a set of 
_Refs_key values.  In this instance I had to take the sql results set, 
iterate over it building the lists for two distinct output bcps.  
Something I would not have been able to do easily using the mgdlib.sql() 
function (w/o resorting to a parser that stored rows to a global 
variable for subsequent processing).

The constructor and write method both have a 'ListOfOutputColumns' argument
in order to allow use where the column list is the same for everything 
being output.  The 'ListOfOutputColumns' is included in the write method
to facilitate cases where multiple dissimilar inputs must be merged into
a common output stream, especially in an inter-leaved manner.

The following class and instance variables can be assigned to change 
default values.  For example, setting:

    BCPWrite.fldSep = '#&#'
    BCPWrite.rowSep = '#=#\n'

will reset the class default delimitors for all subsequent instantiations 
(example delimitors from one we use to unload table where tab, '|' and
newlines might be embedded in the data itself.

You may also assign to a particular instance object's class members to reset
its delimitors:
    mybcp = BCPWrite ( 'myoutput.bcp', None, myListOfOutPutColumns )
    mybcp.fldSep = '\t'
    mybcp.rowSep = '\n'

Clients should not assign directly to the class template member filename!

The preferred way to append multiple inputs on to a single output bcp is
to open the object w/o data, and call the object's write() method for each 
result set, passing a set-specific column list as needed to map each data set 
onto the bcp format/layout.  This can be done iteratively when the multiple
sources depend on each other and cannot be processed sequentially.

The class also supports writing a single row at a time to the bcp file, though
this is discouraged due to the relatively high over-head.

mybcp instance above could be reused multiple times with different output 
sets, simply by calling its write() method for each result set.
     

ATTRIBUTES AVAILABLE OUTSIDE THE CLASS:

fldSep   -- column separator string
rowSep   -- row terminator string.

(READ-ONLY ATTRIBUTES -- DO NOT WRITE DIRECTLY TO THESE!!:)
cols     -- list that defines the output column mapping from the data to 
	    the file -- the init() takes an arg to assign to this attribute.  
	    If an element of the list is NOT a subscript of the data, the 
	    element is output as a literal specification.

fh       -- open file handle for output.

filename -- name of specified output file.


METHODS AVAILABLE THROUGH THE CLASS:

write( data:LIST, colList:LIST--default=None which uses self.cols )
    writes the supplied list of subscriptable objects to the output file.
    Will (re)open file if necessary.  (Output is flushed after each set of
    writes.)

close()
    if the class has an open output file, closes the file and releases
    the object's file handle attribute.

len(aBCPWriteClassInstance)
    returns the number of rows output to the file since it was FIRST opened.

"""

# module defaults:
SEP = "|"
NL = "\n"

from types import *
import re, string, sys, os


class BCPWrite:
    """
      An object with a generic write method to output one or a
      list of rows in bcp format.

      DATA MEMBERS:
	fldSep : string -- delimitor in output columns; user alters if needed.
	rowSep : string -- record delimitor in output; user alters if needed.
	filename : string -- name of file if requested by name; READ ONLY.
	fh : as FILE object -- whether opened by object or passed already
	     opened by caller; READ ONLY.
	iOpened : 'boolean' -- true when object creates the file; READ ONLY.
	rowsOutput : integer -- # rows written to output;
	     PRIVATE (use len(BCPWriteObj)

      METHODS:  (* [] indicate optional args *)
	__init__(f, [row, [columnListOrdering]]):
	    f : either a file name or a file handle (string or FILE object).
	    row : dictionary, list of dictionary, list of simple-types,
		or list of lists.
	    columnListOrdering : list of dictioary keys or other indices
		for accessing the input; controls the order of columns output.

	write(rowOrList): output method; see method header below.
	close(): way to explicitly close the objects output file handle.
	data2SQL(...): conversion method to handle multiple input data types
	loadTable(...): takes the generated output file and loads to specified
		table, server, database, user, pwd.
	__len__() : returns # rows written by object

      USEAGE:
	Class can be used as the iterator function to calls to sybase.sql()
	or initialized and .write() called iteratively or initialized and
	passed a 'block' (list of lists or dictionaries).

      NOTES:
	- Writing to a closed file, causes it to be reopened in append mode.
	- The file need never be explicitly closed; can rely on the destructor
	  to close when object is garbage collected.
    """

    # class defaults
    fldSep = SEP
    rowSep = NL
    filename = None
    fh = None
    error = "BCPWrite.error"

    def __init__ ( self, f, data = None, colOrder = None):
	"""
	Constructor; data and colOrder are optional.  
	data is a Dictionary, or List of Dicts or Lists to be output.
	colOrder is an ordered list of column identifiers
	(dictionary keys) to output from each data row.
	#--------------------------------------------------
	# INPUTS:     
	#    f : FILE (file descriptor) or String (file name)
	#		If an open file handle is passed, it is used as is;
	#	       if a string is passed it is used as a file name.  
	#    data (optional): output object 
	#    colOrder (optional): list of (string or integer) keys -- 
	#	   maps input fields on to output columns.  Items in list
	#	  must be 'indices' for the input row(s)
	# OUTPUTS:     
	# ASSUMES:     
	# SIDE EFFECTS: 
	#   Initializes the applicable instance variables (possibly
	#   including fh, filename and iOpened) depending on the data type
	#   of f.  If data rows (data is not None) then writes the input
	#   data to the output file after formating and mapping 'fields' on 
	#   to columns.
	# EXCEPTIONS: 
	# COMMENTS:  
	#--------------------------------------------------
	"""

	fType = type ( f )
	if fType == StringType:
	    self.fh = open ( f, "w" )		    # reset len to 0
	    self.filename = f
	    self.iOpened = 1
	elif fType == FileType:
	    # assume it's an open file handle
	    self.fh = f
	    self.iOpened = 0

	self.cols = colOrder

	self.rowsOutput = 0
	if data:
	    self.write (data)


    def write ( self, rowObj, colList = None ):
	""" write rowObj to the output file.
	"""
	#--------------------------------------------------
	# INPUTS:     
	#    rowObj : dictionary, list of dict or list of lists; data to output
	#	    11/25 now also accepts a single list as a row to process.
	#   colList : list -- ordering of columns to be output
	# OUTPUTS:     
	#   writes input rows to output file
	#   returns nothing
	# ASSUMES:     
	#   Col and Row separators are compatible with string.join
	# SIDE EFFECTS: 
	#   writes input rows to output file
	# EXCEPTIONS: 
	#   KeyError -- when mapping of dictionary input onto output is invalid.
	#   IndexError -- when mapping of list input onto output is invalid.
	# COMMENTS:  
	# MODIFICATIONS:
	# 11/25/94 rpp: 
	# added 1st elif to handle single row list of columns.
	#--------------------------------------------------

	typeRowObj = type ( rowObj )
	if typeRowObj == DictType:
	    # list-ify it so can iterate regardless of input arg
	    rowList = [ rowObj ]			    # list of 1 dict
	elif typeRowObj == ListType and len(rowObj) == 1 \
	    and type (rowObj[0]) not in (ListType, DictType):
	    # listify a simple list of column-values
	    rowList = [ rowObj ]			    # list of 1 list
	else:
	    # assume sequence type or sequence type compatible class
	    rowList = rowObj		    # list of sequencable-objects
	    
	if not rowObj or len(rowObj) == 0:
	    # there's nothing to output
	    return

	if self.fh is None and self.filename:
	    # if close() method called and object writes more data
	    self.fh = open (self.filename, "a")		# reopen for append
	    # alternatively  we could consider this an error
	
	# if colList supplied use that over anything else.
	# if user supplies no mapping either in the class or this call,
	# default one:
	if colList is None and self.cols is None:
	    if type ( rowObj ) == DictType:
		colList = rowObj.keys()
	    else:
		colList = range ( len(rowList[0]) )
	elif colList is None:
	    # default to objects col mapping
	    colList = self.cols

	row = col = 0

	# for each row in the input object
	for r in rowList:
	    self.rowsOutput = self.rowsOutput + 1	# total output
	    row = row + 1				# cnt this batch
	    line = []

	    # for each column in the mapping on to the output format
	    for c in colList:
		col = col + 1
		try:				    # get output from input
		    if c is None:
			fieldval = None		    # placeholder
		    elif type (r) == DictType:
			if r.has_key( c ):
			    fieldval = r[ c ]
			else:
			    # placeholder "column" w/ no corresponding value
			    # OR literal
			    fieldval = c		  # treat as literal
		    else:
			# for sequence and class types
			fieldval = r [ c ]

		except TypeError:
		    print "row # = %u col # = %u " % (r, c)
		    print "cols = ", colList
		    print "columns = ", rowList.keys()
		    print "row = ", rowList[row]
		    sys.exit(1)
		except KeyError:
		    print "row # = %u col # = %u " % (r, c)
		    print "cols = ", colList
		    print "columns = ", rowList.keys()
		    print "row = ", rowList[row]
		    print "rowList[row].has_key( self.cols[col] ) = ", \
				  rowList[row].has_key( self.cols[col] )
		    sys.exit(1)
		except IndexError:
		    print "row = ", r
		    print "cols = ", colList
		    print "row # = %u col # = %u " % (row, col)
		    print "#cols in row = %u #cols in cols = %u" % (
				len(r), len(colList) )
		    if 0 <= col < len(colList):
			print "colList[col] (aka c) = ", c
		    if 0 <= col < len(r):
			print "row[col] (aka r[c]) = ", r[c]
		    sys.exit(1)

		# build up the output line for each column
		if type ( fieldval ) == StringType:
		    # text fields may have embedded newlines.
		    if self.rowSep == NL:
			line.append ( removeNL (fieldval) )
		    else:
			line.append ( fieldval )
		else:
		    # don't search and replace if not an issue
		    line.append ( self.data2SQL (fieldval) )

	    self.fh.write ( string.join (line, self.fldSep)
			    + self.rowSep )

	# insure set is writen out
	self.fh.flush ()



    def close ( self ):
	""" Close the output file.
	"""
	#------------------------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     
	#    results from self.fh.close() OR None if fh is None.
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	tmp = self.fh
	self.fh = None
	# unclear when self.rowsOutput should be reset
	if tmp != None:
	    return tmp.close()
	else:
	    return None



    def loadTable ( self,
		    tableName,
		    server,
		    database,
		    user,
		    pwd,
		    bcpFileName = None
		    ):
	#------------------------------------------------------------------
	# INPUTS:
	#   tableName : string -- name of the destination table
	#   server    : string -- name of target SQL server
	#   database  : string -- name of target DB
	#   user      : string -- SQL login user ID
	#   pwd       : string -- SQL login password
	#   bcpFileName : string -- name of bcp file (optional if object
	#                           knows its file's name.
	# OUTPUTS:
	#   returns the number of rows written to the BCPfile
	# ASSUMES:
	# - that bcp utility is available w/o a specific path
	# SIDE EFFECTS:
	# -  transfers contents of the bcp file to the specified table.
	# EXCEPTIONS:
	# - raises BCPWrite.error if cannot find a bcp file, or errors in load
	# COMMENTS:
	# - It is not possible to guarantee that we've caught all load  errors
	#   since bcp does not return any error code when it fails for any 
	#   reason and in some cases doesn't even write to the error log.
	#------------------------------------------------------------------
	
	# if the object has an explicit name, use it; otherwise assume
	# caller knows the file name that the object wrote to
	if self.filename is not None:
	    bcpFileName = self.filename
	elif not bcpFileName:
	    # object opened with an open file and user didn't supply the name
	    raise self.error, "BCPWrite.loadTable(): BCP File name required!"

	if self.fh is not None:
	    # the output must be closed prior to loading to a talbe!
	    msg = "BCPWrite.loadTable(): output file %s still open!"
	    if self.filename:
		msg %  ( "(" + self.filename + ")" )
	    else:
		msg % ""
	    raise self.error, msg
	elif self.rowsOutput > 0:
	    errFile = bcpFileName + ".error"
	    cmd = "rm -f %s; echo %s | bcp %s..%s in %s -S %s " \
		  "-U %s -c -t '%s' -r '%s' -e %s -m 1" \
		  % ( errFile,
		      pwd,
		      database,
		      tableName,
		      bcpFileName,
		      server,
		      user,
		      self.fldSep,
		      self.rowSep,
		      errFile
		      )
	    cmdStatus = os.system ( cmd )
	    if cmdStatus or os.path.isfile ( errFile ):
		errMsg = "BCPWrite.loadTable(): bcp exit status = %d\n%s\n" \
			 % ( cmdStatus, cmd )
		if os.path.isfile ( errFile ):
		    errMsg = errMsg + string.join (
			open(errfile).readlines(), NL
			)
		raise self.error, errMsg
		    
	return self.rowsOutput



    def __del__ ( self ):
	""" Destructor insures output file (fh) is closed.
	"""
	#------------------------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     none
	# ASSUMES:     
	# SIDE EFFECTS: 
	#   closes fh if not None.
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	if self.fh and self.iOpened: 
	    self.close()


    def __len__ ( self ):
	""" Returns the totoal number of rows written by instance.
	"""
	#------------------------------------------------------------------
	# INPUTS:     none
	# OUTPUTS:     int -- # rows written by this instance variable
	# ASSUMES:     
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	return self.rowsOutput


    def data2SQL ( self, val, nullVal = "", removeNewLine = 0 ):
	"""
	string conversion utility for polymorphic input 'val' arg.
	Handles numerics, dates as python tuples, and strings which might
	include embedded quote chars.
	"""
	#--------------------------------------------------
	# INPUTS:     
	#    val : polymorphic
	#    nullVal : string -- what string to substitute if val is null.
	#    removeNewLine : boolean -- do extra processing to remove embedded 
	#	    newlines.
	# OUTPUTS:     
	#    returns a string representation of the input suitable to use w/ SQL
	#    and bcp text.
	# ASSUMES:     
	# -  input val is one of the recognized data types.
	# -  that strings DO NOT contain embedded colSep substrings.
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	# NOTE:
	#   embedded TABs and colSep strings are not translated here.
	#--------------------------------------------------

	t = type(val)

	if t is NoneType:
	    return nullVal

	elif t is StringType:
	    # chk for embedded quote chars (either single or double quotes
	    # if "'" not embedded, surround with '
	    # elif '"' not embedded, surround with "
	    # else double up existing ' and surround with '
	    if removeNewLine:
		val = string.join ( string.split ( val, NL ), " " )
	    singleQuote = string.count ( val, "'" )
	    doubleQuote = string.count ( val, '"' )
	    if singleQuote > 0 and doubleQuote > 0:
		# replace all standalone single quotes with double single quotes
		#    couldn't get | pattern "(^|[^'])'($|[^'])" to work...
		# leading , trailing and embedded:
		val = re.sub ("^'[^']", "''", val)
		val = re.sub ("[^']'$", "''", val)
		return "'" + re.sub ("[^']'[^']", "''", val) + "'"
	    elif singleQuote > 0:
		return '"' + val + '"'

	    else: 
		# use single quotes around string
		return "'" + val + "'"

	elif t is TupleType:
	    # assume tuple is a date: (yyyy, mm, dd)
	    if len(val) == 3:
		datestr = "%d/%d/$d" % val
		# (yr, mo, day) = val
		# datestr = str(yr) + "/" + str(mo) + "/" + str(day)
	    elif len(val) > 3:
		# take the first 5 args as YYYY, MM, DD, HH, mm, SS
		datestr = "%d/%d/%d %d:%d:%d" % val[:5]
		# (yr, mo, day, hr, min, sec) = val
		# datestr = str(yr) + "/" + str(mo) + "/" + str(day) + " "     \
		#	+ str(hr) + ":" + str(min) + ":" + str(sec)
	    else:
		print "ERROR: Unexpected date-time format:", val
		datestr = ""

	    return datestr

	else:
	    return str(val)

########################################################################

def removeNL ( s, replacement = " " ):
    """ substitute specified replacement string for Newline characters;
	replacement defaults to " ".
    """
    #--------------------------------------------------
    # INPUTS:
    #    s as string;
    #    replacement (optional) : string -- defaulted to a single space
    # OUTPUTS:     string w/ newlines replaced 
    # ASSUMES:     
    # -   inputs are compatible w/ string.join & string.split
    # -   NL is globally defined & initialized.
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #--------------------------------------------------

    if string.find ( s, NL) > -1:

	s = string.join ( string.split (s, NL), replacement )

    return s


