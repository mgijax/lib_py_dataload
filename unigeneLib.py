#! /usr/local/bin/python

############################################################################
# Copyright (C) 1999 The Jackson Laboratory
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
Description:
Library module supporting UniGene Accession Load and Putatives based on
UniGene clusters.  The module's primary public functions provide single
function calls to provide a list of putative associations and Unigene
cluster links associated with mouse genes.  An init() routine provides
for initialization of module global objects that the high level functions
rely on.

The module's two data instances provide mapping/associations
between UniGene cluster-associated SIDs with MGD mouse gene-associated SIDs.

Module supports running in test mode.  It accepts command line options
to override the default file names for the UniGene Cluster-SIDs and
dbEST/WashU clone-putatives files.
    
Syntax:

import unigeneLoad

unigeneLoad.init ( <UniGeneInputFile>,    ## file name
		   <retrvOption>,         ## -1, 0, 1 (see func hdr.)
		   <MarkerTypeFilterTupe> ## ( boolean, [ GeneTypeNames ] )
		   )
...
while line:
    ...
    putativeList = unigeneLoad.getPutativeGenes ( <SomeGenBankSID> )
    ...


Options: (command-line test mode only)
 -i <clone-GenBankSID file name>
 -u <UniGene_Cluster-SIDs file name>
"""

############################################################################
# AUTHOR:  R. Palazola
# DATE:    9/21/1999
# VERSION: %W%
#
# PURPOSE: <see __doc__ string above>
#---------------------------------------------------------------------------
# USAGE: <see __doc__ string above>
#
#---------------------------------------------------------------------------
# INPUT FORMAT(s):
# UniGene Cluster-SIDs File:
#  A multi-line, text record with each attribute identified by a leading
#  keyword.  We are interested in only the UniGene Cluster ID ("ID") and
#  the associated SIDs ("SEQUENCE" subfield "ACC=" -- subfield is semi-colon
#  delimited.)
#
# Test Input data file (command-line test mode)
#  A "|"-delimited text file consisting of the clone's IMAGE ID, WashU ID
#  and the associated GenBank SID.
#
#---------------------------------------------------------------------------
# PROCESSING -- what it does with the input:
#
#---------------------------------------------------------------------------
# DEFINITIONS:
# - SID -- Sequence ID -- a GenBank sequence ID
# - UG  -- UniGene, an abbreviation.
#
#---------------------------------------------------------------------------
# ASSUMPTIONS:
#
#---------------------------------------------------------------------------
# MODIFICATIONS:
#
############################################################################


############
# IMPORTS:
#-----------
import string, sys, os
import mgdlib		# , accessionLoadUtils
from types import *

# local aliases:
sql = mgdlib.sql
## DBLookUp = accessionLoadUtils.DBLookUp


############
# CONSTANTS:
#-----------
NL      = "\n"
TAB	= "\t"
SEQDB	= 9			# _LogicalDB_key for Seq. DB

############
# MODULE GLOBALS
#-----------
# Directory Path in which to look for the download file:
gUGdir       = "repository/UniGene"
# UniGene's FTP server:
gUGftpServer = "ftp.ncbi.nlm.nih.gov"
gUGZFileName = "Mm.data.Z"

# used by callback function supplied to FTP.retrvbinary() 
gUGftpFile   = None

ug = None	# SID-cluster(s) associative ADT object
mgiSids = None  # MGD GenBank-2-Markers object

############
# MODULE PUBLIC FUNCTIONS
#-----------

def init ( ugFile, retrieve=-1, loadFilter=None ):
    #------------------------------------------------------------------
    # INPUTS:
    #   ugFile : None or string (FileName) OR FILE (already opened)
    #   retrieve : -1, 0, 1 (-1 = never (do not download from UniGene)
    #                         0 = if missing (download if file does not exist)
    #                         1 = always download from UniGene regardless
    #                             of whether file exists or not.
    #   loadFilter : pass through to MGI_SIDs.load()
    # OUTPUTS: none
    # ASSUMES: 	
    # SIDE EFFECTS:
    # - if downloaded, overwrites an existing Unigene data file
    # - initializes the two module data objects for use by the public
    #   module functions
    #   
    # EXCEPTIONS: 
    # COMMENTS:  
    #------------------------------------------------------------------

    global ug, mgiSids 
    

    ug = UniGeneSIDs()
    mgiSids = MGI_SIDs()

    ugFileArgType = type (ugFile)

    if ugFileArgType is FileType:
	ugExists = 1
    elif ugFileArgType is StringType:
	ugExists =  os.path.isfile ( ugFile )
    else:
	raise AttributeError,  \
	      "%s.init(): must be file name or file object." % __name__

    if retrieve == 1 or ( retrieve == 0 and not ugExists ):
	# useExisting arg to getUGfile is opposite of retrieve value of 0 or 1:
	ugfh = getUGfile ( ugFile, 0 )
	if ugfh is None:
	    raise IOError, "Cannot open UniGene input %s" % ugFile

    elif ugFileArgType is StringType and ugExists:
	try:
	    ugfh = open ( ugFile, "r" )
	except IOError, msg:
	    sys.stderr.write (
		"%s: cannot open UniGene input file: %s\n"
		% ( __name__, ugFile )
		)
	    sys.stderr.flush()
	    raise IOError, msg
    elif ugFileArgType is FileType:
	ugfh = ugFile
	# redundant
##      else:
##  	raise AttributeError, "Expecting File name or File object."

	
    # load available Unigene SID-Cluster associations
    ug.load ( ugfh )

    # load MGD SID-Marker associations
    mgiSids.load ( loadFilter )

    return



def ftpFileWriter ( block ):
    #------------------------------------------------------------------
    # Callback function for FTP instance.
    # INPUTS: 	text block
    # OUTPUTS: 	None
    # ASSUMES: 	
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #------------------------------------------------------------------
    gUGftpFile.write ( block )
    return


def getUGfile ( ugFilename, useExisting ):
    #------------------------------------------------------------------
    # INPUTS:  ugFilename : string -- path & file name for input file
    #	       useExisting : boolean -- false downloads fresh copy from UniGene
    # OUTPUTS: f : FILE obj or None	
    # ASSUMES:
    # - UniGene's ftp site is available and responsive
    # - global varibles define the ftp site, path and file name
    # - that desired compressed file available at UniGene ftp site
    # - desired ftp file is actually in a compressed format (".Z")
    # SIDE EFFECTS:
    # - if downloads file, will overwrite an existing <ugFilename>.
    # EXCEPTIONS: 
    # COMMENTS:  
    #------------------------------------------------------------------

    global gUGftpFile				# for update
    global gUGZFileName				# readonly
    f = None
    
    if not useExisting:
	
	from ftplib import FTP, all_errors

	# get the local path and root filename via os.path.split()
	(localPath, ugfile) = os.path.split(ugFilename)
	# form a pathed local file name
	localZfile = os.path.join ( localPath, gUGZFileName )
	# open a destination file for the ftp download
	gUGftpFile = open ( localZfile, "w" )

	# download the compressed file
	ug = FTP ( gUGftpServer )
	ug.login()				# anonymous
	ug.cwd (gUGdir )
	ug.retrbinary ( "RETR " + gUGZFileName ,	# compressed form
			ftpFileWriter,		# writer callback function
			10240	    # newer python does not require block size.
			)
	try:
	    # polite request
	    ug.quit()
	except all_errors:
	    # unilaterally terminate connection
	    ug.close()
	    
	gUGftpFile.close()
	gUGftpFile = None

	# should protect the former copy & delete the former back up
	# decompress the file, forcing overwrite of existing file 
	os.system ( "uncompress -f %s" % localZfile )
	# name it per input request; assumes that the uncompressed file
	# name is less the .Z extension.
	os.rename ( localZfile[:-2], ugFilename )

    if os.path.isfile ( ugFilename ):
	f = open ( ugFilename, "r" )
    return f



def getPutativeGenes ( sid ):
    #------------------------------------------------------------------
    # INPUTS: sid -- string
    # OUTPUTS:
    #   None | List of Tuples ( _Marker_key, symbol ) that putatively
    #   associate with the given SID.
    #   None indicates that there are no associated SIDs for the given SID;
    #        i.e., there's no UG cluster with a matching SID
    #   [] indicates that there was a match to one (or more) clusters
    #      but that none of the associated SIDs map to a marker.
    #   [...] is a list of the gene info Tuples that putatively associate
    #      with the given SID.
    # ASSUMES: 	
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:
    # - return values:
    #     - None implies that the sid is not in any UG cluster
    #     - [] implies that sid was found in a cluster or clusters but
    #       not MGI mouse gene markers are associated with any of the
    #       SIDs in those clusters.
    #     - Non-empty lists of tuples of gene info for putative assoc.
    #   
    #------------------------------------------------------------------

    putatives = None
    ugSIDs = ug.getAssociatedSIDs ( sid )
    
    if ugSIDs:
	putatives = []

	for ugsid in ugSIDs:

	    genes = mgiSids.getMGIinfo ( ugsid )
	    if genes:
		for info in genes:
		    # more than 1 SID can produce same geneInfo
		    # only insert unique gene associations
		    if info not in putatives:
			putatives.append ( info )
    return putatives



def getMGI_SIDsObjectReference ():
    #------------------------------------------------------------------
    # INPUTS: 	None
    # OUTPUTS: 	reference to module's MGI_SIDs instance
    # ASSUMES:
    # - that a user who get's the module's object will not modify the
    #   data structure through the reference.
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:
    # Public function for access to module's SID-mouse Gene associations
    # data member.
    #------------------------------------------------------------------
    return mgiSids


def getUGObjectReference ():
    #------------------------------------------------------------------
    # INPUTS: 	None
    # OUTPUTS: 	reference to module's UniGeneSIDs instance
    # ASSUMES: 	
    # - that a user who get's the module's object will not modify the
    #   data structure through the reference.
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:
    # Public function for access to module's SID-UniGene associations
    # data member.
    #------------------------------------------------------------------
    return ug




############
# MODULE CLASSES
#-----------

class UniGeneSIDs:
    ## the UniGeneSIDs is an associative ADT that supports querying the 
    ## UniGene cluster/SID information to determine both to which cluster
    ## a given SID belongs ( possibly more than one), and for any given
    ## cluster which SIDs are associated with it.  The goal is to get
    ## a list of associated SIDs for a supplied specific SID.
    ##
    #######################################################################
    # DATA MEMBERS:
    # (private) _sid2Clusters : dictionary of lists of cluster IDs keyed by SID
    # (private) _cluster2SIDs : dictionary of lists of SIDS keyed by cluster ID
    #
    # METHODS:
    # (PUBLIC)
    # getAssociatedSIDs ( sid) /*, uniqueFlag)*/ : list of SIDs
    # getClusterIDs () : list of cluster ID keys in the assoc. data struct.
    # getClustersForSID ( sid ) : list of cluster ID(s) for this sid
    # getSIDs () : list of unique SIDs in the associative data structure
    # length ()  : string -- debugging; shows counts for the two dictionaries
    # load ( fd:FILE ) -- loads data structure from specified file
    #
    # (PRIVATE)
    # readRecord ( fd:FILE ) : Tuple (UniGene ID, List of SIDs)
    #
    # USEAGE:
    #
    # NOTES:
    # - User/caller should _NOT_ modify the returned lists from this object
    #   as most would modify the object's internal data, invalidating the
    #   data as loaded from the input file. Generally, the list are needed
    #   for iteration over, not for modifications of the list's contents.
    # - methods that return lists have been optimized to return references
    #   to the internal lists (instead of the preferred list copying) as a
    #   performance optimization.
    #
    # ASSUMES:
    #
    # MODIFICATIONS:
    #######################################################################
    
    
    _sid2Clusters = None	# dict of cluster IDs keyed by SID
    _cluster2SIDs = None	# dict of lists of SIDs keyed by cluster IDs

    def __init__ ( self ):
	self._sid2Clusters = {}
	self._cluster2SIDs = {}
	return

    def getAssociatedSIDs ( self, sid, uniqueCluster=0 ):
	#------------------------------------------------------------------
	# INPUTS:
	#   sid : string -- the Sequence ID to look up
	#   uniqueCluster: boolean -- whether or not to expand sid-cluster
	#                             associations when the sid appears in
	#                             multiple clusters
	# OUTPUTS: a list of all sids associated via UniGene cluster(s)
	#          to the argument SID or an empty list if none qualify.
	# ASSUMES: 
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:
	#   The elif could do both jobs with an or'd if test but this
	#   causes the list to be copied to another list; the separate
	#   code eliminates a needless element-wise copy when the list
	#   is only 
	#------------------------------------------------------------------

	sids = []
	uids = self.getClustersForSID ( sid )
	if len(uids) == 1:
	    sids = self.getSIDsForUid ( uids[0] )
	elif not uniqueCluster and len(uids) > 1:
	    for uid in uids:
		# accummulate the sids
		sids = sids + self.getSIDsForUid ( uid )

	return sids
    

    def getClusterIDs ( self ):
	#------------------------------------------------------------------
	# INPUTS:  none
	# OUTPUTS: list of the cluster IDs in the ADT
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	return self._cluster2SIDs.keys()


    def getClustersForSID ( self, sid ):
	#------------------------------------------------------------------
	# INPUTS:  sid : string
	# OUTPUTS: list of the cluster IDs associated with given SID.
	# ASSUMES:
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:
	# - Returns a reference to the desired list, instead of a copy;
	#   this is done strictly for performance reasons and the caller
	#   should not use the list reference to alter the contents of
	#   the list.
	#------------------------------------------------------------------
	if self._sid2Clusters.has_key ( sid ):
	    return self._sid2Clusters [ sid ]

	return []


    def getSIDs ( self ):
	#------------------------------------------------------------------
	# INPUTS:  none
	# OUTPUTS: list of the SID keys in the ADT
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	return self._sid2Clusters.keys()


    def getSIDsForUid ( self, uid ):
	#------------------------------------------------------------------
	# INPUTS:  uid : string -- Unigene Cluster ID
	# OUTPUTS: list of the SIDs in the ADT for the given cluster ID.
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	# - Returns a reference to the desired list, instead of a copy;
	#   this is done strictly for performance reasons and the caller
	#   should not use the list reference to alter the contents of
	#   the list.
	#------------------------------------------------------------------
	if self._cluster2SIDs.has_key ( uid ):
	    return self._cluster2SIDs [ uid ]
	
	return []


    def length ( self ):
	return "SID keys %u; UGID keys %u" % ( len (self._sid2Clusters),
					       len (self._cluster2SIDs)
					       )


    def load ( self, fd ):
	#------------------------------------------------------------------
	# INPUTS:
	#    fd : FILE -- input from which to load the ADT
	# OUTPUTS: 
	# ASSUMES: 	
	# SIDE EFFECTS: populates class's data members
	# EXCEPTIONS: raises KeyError on duplicate Cluster IDs 
	# COMMENTS:
	# - SIDs may appear in multiple clusters, AND, there are instances
	#   of the same SID appearing in a single cluster more than once.
	#------------------------------------------------------------------
	rec = self.readRecord (fd)
	while rec:
	    (ugid, seqList) = rec
	    # each cluster ID should be unique
	    if self._cluster2SIDs.has_key ( ugid ):
		raise KeyError, "Duplicate cluster ID %s" % ugid
	    else:
		self._cluster2SIDs [ ugid ] = seqList

	    # however, SIDs might be in more than one cluster
	    for sid in seqList:
		if self._sid2Clusters.has_key ( sid ):
		    self._sid2Clusters[sid].append (ugid)
		else:
		    self._sid2Clusters [ sid ] = [ ugid ]

	    rec = self.readRecord (fd)

	return


    def readRecord ( self, fd ):
	#------------------------------------------------------------------
	# INPUTS: FILE reference
	# OUTPUTS: TUPLE ( UGid, SIDList )	
	# ASSUMES: 	
	# SIDE EFFECTS: reads a set of lines from input file
	# EXCEPTIONS: 
	# COMMENTS:
	# - Input records can contain multiple SEQUENCE fields for same SID.
	#   Added code to append only 1st instance of any given SID
	# - Commented out code was for extracting more information from input;
	#   this information is no longer used.
	#------------------------------------------------------------------
	rec = ugid = gene = assertedMGIids = None
	sequenceList = []
	line = fd.readline ()
	while line and line[:-1] != "//":
	    words = string.split (line[:-1])
	    tag = words[0]
	    if tag == "ID":
		ugid = words[1]
	    elif tag == "SEQUENCE" and words[1][:4] == "ACC=":
		# extract the GenBank ID from form "ACC=.*;" & accummulate
		sid = words[1][4:-1]
		sequenceList.append ( sid )

	    line = fd.readline()

	if ugid:
	    rec = ( ugid, sequenceList )
	return rec





class MGI_SIDs:
    """An MGI_SIDs is a marker look-up mechanism for specified Sequence
    accession ID.
    """
    #######################################################################
    # DATA MEMBERS:
    # (private)
    #  _markerInfo   : dictionary of marker info records keyed by marker key;
    #                  the marker info records are represented as tuples of
    #                  related information (markerKey, symbol, MGI_ID?,...?)
    #  _sids2Markers : dictionary of list of marker info record references
    #                  keyed by SID
    #
    # METHODS:
    # (PUBLIC)
    #  getMGIinfo ( sid ) : List (elements are the desired marker info)
    #  length () : string -- debugging; message w/ # entries in the dict.
    #  load ( MarkerFilterTuple : (boolean, List of strings) --
    #             gets SID-marker information from default MGD instance;
    #             populating the class's dictionary with (_Marker_key, symbol)
    #             entries keyed by SID.
    # (PRIVATE)
    # sidParser (row:Dict) -- parser function for load()'s SQL query.
    #
    # USEAGE:
    #
    # NOTES:
    # - The _markerInfo dictionary is intended to allow multiple _sids2Markers
    #   entries to reference a single copy of the marker info.  It is expected
    #   that the marker info record might also include other information,
    #   especially the markers' MGI IDs. This is an attempt to reduce the
    #   memory required for these data structures.
    #
    # ASSUMES:
    #
    # MODIFICATIONS:
    #######################################################################

    # CLASS CONSTANTS:
    MARKERPOS = 0		# tuple-position of marker key
    SYMBOLPOS = 1		# tuple-position of marker symbol
    
    def __init__ ( self ):
	self._sids2Markers = {}
	self._markerInfo   = {}
	return

    def getMGIinfo ( self, sid ):
	#------------------------------------------------------------------
	# INPUTS: sid : string
	# OUTPUTS: List of Marker-Info Lists
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	# - Returns a reference to the desired list, instead of a copy;
	#   this is done strictly for performance reasons and the caller
	#   should not use the list reference to alter the contents of
	#   the list.
	#------------------------------------------------------------------
	data = []
	if self._sids2Markers.has_key (sid):
	    data = self._sids2Markers[sid]
	return data
    

    def length ( self ):
	return "SID keys %u" % len(self._sids2Markers)


    def load ( self, markerTypeTuple ):
	#------------------------------------------------------------------
	# INPUTS:
	#    markerTypeFilter : string or None
	# OUTPUTS: none
	# ASSUMES:
	# - That mgdlib.sql() can access needed environment variables in order
	#   to determine a default server/database.
	# SIDE EFFECTS: populates the class's primary, internal data members
	#               from the default MGD instance.
	# EXCEPTIONS: 
	# COMMENTS:
	# - The commented out code is for more complete marker information,
	#   including the marker's preferred MGI ID.
	#------------------------------------------------------------------

	# this function private to doing the load:
	def markerType2SQL ( typeTuple ):
	    filterString = ""
	    if typeTuple:
		( sense, typeList ) = typeTuple

		qry = ( "select _Marker_Type_key from MRK_Types "
			"where name in ( %s ) "
			% str(typeList)[1:-1]
			)
		geneTypes = []
		mgdlib.sql ( qry,
			     lambda row, d=geneTypes:
			     d.append ( row["_Marker_Type_key"] )
			     )

		if len (typeList) == 1:
		    typeString = geneTypes[0]
		    if not sense:
			op = " != "
		    else:
			op = " = "
		else:
		    if not sense:			# not in logic
			op = " not in "
		    else:
			op = " in "
		    typeString = " ( %s ) " % str(geneTypes)[1:-1]


		filterString = ( filterString 
				 + " _Marker_Type_key %s %s "
				 % ( op, typeString )
				 )


	    return filterString


	# for significant marker info
	qry = ( "select distinct symbol, sid = accID, "
		"_Marker_key = _Object_key "
		"from ACC_Accession a, MRK_Marker m "
		"where _LogicalDB_key = %u "
		" and _MGIType_key = 2 "
		" and _Marker_key = _Object_key "
		% SEQDB
		)

	if markerTypeTuple:
	    # and on the marker-type filter specification
	    qry = qry + " and ( %s ) " % markerType2SQL ( markerTypeTuple )
	sql ( qry, self.sidParser )
	
	return


    def sidParser ( self, row ):
	#------------------------------------------------------------------
	# INPUTS:  Dict -- SQL-tuple from query result set
	# OUTPUTS: none
	# ASSUMES: 	
	# SIDE EFFECTS: inserts/appends marker info to dict data member.
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	sid    = row["sid"]
	markerKey = row["_Marker_key"]
	symbol = row["symbol"]
	info = [ markerKey, symbol ]

	# same unique copies of the marker info record
	if self._markerInfo.has_key ( markerKey ):
	    info = self._markerInfo [ markerKey ]
	else:
	    info = ( markerKey, symbol )
	    self._markerInfo[ markerKey ] = info

	if self._sids2Markers.has_key ( sid ):
	    # the same marker info record may result from different SIDs
	    if info not in self._sids2Markers[sid]:
		# add once only
		self._sids2Markers [sid].append ( info )
	else:
	    self._sids2Markers [sid] = [ info ]
	    
	return


############
# MAIN:
#-----------

if __name__ == "__main__":

    def lapsedTime ( tStart ):
	secsPerHour = 3600
	secsPerDay  = secsPerHour * 24

	tMark = time.clock()
	tdiff = tMark - tStart
	days = hrs = mins = secs = 0
	if tdiff> secsPerDay:
	    days = tdiff / secsPerDay
	    tdiff = tdiff % secsPerDay
	if tdiff > secsPerHour:
	    hrs = tdiff / secsPerHour
	    tdiff = tdiff % secsPerHour

	if tdiff > 60:				# secs in a minute
	    mins = tdiff / 60
	    tdiff = tdiff % 60

	secs = tdiff

	st = ""
	if days: st = "%u days " % days
	st = st + "%u hours %u mins %4.1f secs" % ( hrs, mins, secs )
	return (tMark, tMark-tStart, st)

	
    import getopt, time

    (opts, args) = getopt.getopt ( sys.argv[1:], "hu:i:" )


    ugFile    = "Mm.data"
    dbESTFile = "dbESTputatives.out"
    
    ugfd = dbESTfd = None
    
    for (opt, value) in opts:
	if opt == "-u":
	    ugFile  = value
	elif opt == "-i":
	    dbESTFile = value
	elif opt == "-h":
	    print __doc__
	    sys.exit (1)

    print mgdlib.date(), "\n"

    # defaults files
    if ugfd is None and ugFile:
	print "Will get UniGene SID-Cluster associations from", ugFile
	ugfd = open (ugFile, "r")

    print "Initializing UniGene SID-Cluster and "\
	  "MGD SID-Gene associative lists..."
    # load using restriction that Marker Types be Gene only!
    init ( ugfd, -1, (1, ["Gene"]) )

    cntClones = \
	      cntNoMGDmatch = \
	      cntNoUGmatch = \
	      cntPutatives = \
	      cntAmbigClusters = 0

    # now iterate over the dbEST input and report which IMAGE clones
    # get putatives to which MGI genes

    if dbESTfd is None and dbESTFile:
	print "Reading dbEST Clone/EST/GenBank SID from", dbESTFile
	dbESTfd = open ( dbESTFile, "r" )

    prbmrkr = open ( "./PRB_Marker.out", "w" )
    timeRec = open ( "./unigeneLoad.times", "w" )

    line = dbESTfd.readline ()
    t = tStart = time.clock()
    
    while line:
	cntClones = cntClones + 1

	if cntClones % 1000 == 0:
	    (t, secs, tstring) = lapsedTime (tStart)
	    msg = "%u records %s lapsed time %4.2f recs/sec" % (cntClones,
							     tstring,
							     cntClones/secs
							     )
	    print msg
	    timeRec.write ( msg + NL )
	    
	words = string.split ( line[:-1], "|" )

	if len(words) > 1 and words[1]:
	    ( mgiPrbKey, llnlID, gbID ) = tuple(words)
	    putatives = getPutativeGenes ( gbID )
	    if putatives:
		cntPutatives = cntPutatives + 1
		for markerInfo in putatives:
		    marker = markerInfo[MGI_SIDs.MARKERPOS]
		    symbol = markerInfo[MGI_SIDs.SYMBOLPOS]
		    prbmrkr.write ( "%s|%s|\n" % (llnlID, marker) )
##  		    print "IMAGE clone '%s'/ GenBank ID '%s'" \
##  			  " gives putative to '%s' (%u) " \
##  			  % ( llnlID, gbID, symbol, marker )

	line = dbESTfd.readline()

    # end while

    (t, secs, tstring) = lapsedTime (tStart)
    msg = "%u records %s lapsed time %4.2f recs/sec" % (cntClones,
						     tstring,
						     cntClones/secs
						     )
    print msg
    timeRec.write ( msg + NL )
    
    prbmrkr.close()
    print "%10u...Clone records" % cntClones
    print "%10u...clones with putative(s)" % cntPutatives

