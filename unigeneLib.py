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

Syntax:

import unigeneLoad

unigeneLoad.init ( <UniGeneInputFile>,    ## file name
		   <MarkerType> 	  ## Marker Type
		   )
...
while line:
    ...
    putativeList = unigeneLoad.getPutativeGenes ( <SomeGenBankSID> )
    ...

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
# 01/21/2000 rpp:
# - made all sid accesses case insensitive (loading and retrieving)
# 01/20/2000 rpp:
# - Added getSymbols(), and getInfoByKey() to MGI_SIDs class.
#
############################################################################


############
# IMPORTS:
#-----------
import string, sys, os
import db
from types import *

############
# CONSTANTS:
#-----------
SEQDB	= 9			# _LogicalDB_key for Seq. DB

############
# MODULE GLOBALS
#-----------
ug = None	# SID-cluster(s) associative ADT object
mgiSids = None  # MGD GenBank-2-Markers object

############
# MODULE PUBLIC FUNCTIONS
#-----------

def init ( ugFile, loadFilter=None ):
    #------------------------------------------------------------------
    # INPUTS:
    #   ugFile : None or string (FileName) OR FILE (already opened)
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

    # don't reinitialize
    if ug and mgiSids:
	return
    
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

    if ugFileArgType is StringType and ugExists:
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

    # load available Unigene SID-Cluster associations
    ug.load ( ugfh )

    # load MGD SID-Marker associations
    mgiSids.load ( loadFilter )

    return


def findCommonSIDs ( clusterList ):
    #------------------------------------------------------------------
    # INPUTS:
    #    clusterList : List of Cluster IDs (strings)
    # OUTPUTS:  List of Seq IDs that are common to all clusters in list
    #  
    # ASSUMES: 	
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #------------------------------------------------------------------

    common = ug.getSIDsForUid ( clusterList[0] )

    # for each subsequent cluster ID
    for cluster in clusterList[1:]:
	clusterSIDs = ug.getSIDsForUid ( cluster )
	# for each sid still in the common list
	# since we may alter the list, step over a copy
	for sid in common[:]:
	    # if it doesn't appear in this cluster's list...
	    if sid not in clusterSIDs:
		# remove it from the common list
		common.remove ( sid )

    return common

def getPutativeGenes ( sid ):
    #------------------------------------------------------------------
    # INPUTS: sid -- string
    # OUTPUTS:
    #   None | Dictionary of _Marker_keys that putatively associate with the given SID.
    #   None indicates that there are no associated SIDs for the given SID;
    #        i.e., there's no UG cluster with a matching SID
    #   {} indicates that there was a match to one (or more) clusters
    #      but that none of the associated SIDs map to a marker.
    #   {...} is a dictionary of the gene keys that putatively associate
    #      with the given SID.
    # ASSUMES: 	
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:
    # - return values:
    #     - None implies that the sid is not in any UG cluster
    #     - {} implies that sid was found in a cluster or clusters but
    #       not MGI mouse gene markers are associated with any of the
    #       SIDs in those clusters.
    #     - Non-empty dictionary of gene keys for putative assoc.
    #   
    #------------------------------------------------------------------

    putatives = None
    ugSIDs = ug.getAssociatedSIDs ( string.upper ( sid ) )
    
    if ugSIDs:
	putatives = {}
	for ugsid in ugSIDs:
	    genes = mgiSids.getMGIinfo ( ugsid, 1 )
	    if genes:
		for info in genes:
		    # more than 1 SID can produce same geneInfo
		    # only insert unique gene associations
		    key = info[MGI_SIDs.MARKERPOS]
		    if not putatives.has_key(key):
			putatives[key] = None

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
    # getSIDsForUid ( UniGeneCluster_ID ) : list of SIDs
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
	uids = self.getClustersForSID ( string.upper ( sid ) )
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
	sid = string.upper ( sid )
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
	    # convert each entry to force all upper case.
	    seqList = map ( string.upper, seqList )
	    
	    # SIDs might be in more than one cluster ...
	    for sid in seqList[:]:
		
		if not self._sid2Clusters.has_key ( sid ):
		    # first cluster w/ this sid:
		    self._sid2Clusters [ sid ] = [ ugid ]
		    
		elif ugid in self._sid2Clusters[ sid ]:
		    # ... or in same cluster more than once...
		    # don't add reduncantly,
		    # ... and remove duplicate from SID list
		    seqList.remove ( sid )
		    
		else:
		    self._sid2Clusters[sid].append (ugid)

	    # ... however, each cluster ID should be unique
	    if self._cluster2SIDs.has_key ( ugid ):
		raise KeyError, "Duplicate cluster ID %s" % ugid
	    else:
		self._cluster2SIDs [ ugid ] = seqList

	    rec = self.readRecord (fd)

	return


    def splitSeqIdV(self, seqIdVersion):      # String - seqId.version

        # Purpose: split 'seqIdVersion' into seqId and version
        # Returns: list of two strings - 1) seqId 2) version
        # Assumes: nothing
        # Effects: nothing
        # Throws: nothing
        # Example1: seqId, version = splitSeqIdV('AC002397.1')
        #           seqId = 'AC002397'
        #           version = '1'
        # Example2: seqId, version = splitSeqIdV('AC002397')
        #           seqId = 'AC002397'
        #           version = ''

        index = string.find(seqIdVersion, '.')
        if index == -1:
                return [seqIdVersion, '']
        else:
                seqId = seqIdVersion[0:index]
                version = seqIdVersion[index+1:]
                return [seqId, version]

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
		tempid = words[1][4:-1]
		[sid, version] = self.splitSeqIdV(tempid)
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
    #  _markers2sids : dictionary of list of SIDs keyed by marker symbol
    #
    # METHODS:
    # (PUBLIC)
    #  getInfoByKey ( mKey ) : LIST of marker info
    #  getMGIinfo ( sid, oneToOneFlag, [fldname] ) : List (
    #                     elements are the desired marker info)
    #  getMGIkeys () : List of _Marker_key values in _markerInfo dictionary.
    #  getSIDkeys () : List of SID values in _sids2Markers.
    #  getSIDsForMarker ( s ) : list of SIDs for the symbol
    #  getSymbols () : List of symbols in _markers2sids
    #  length () : string -- debugging; message w/ # entries in the dict.
    #  load ( MarkerFilterTuple : (boolean, list of strings) ) --
    #             gets SID-marker information from default MGD instance;
    #             populating the class's dictionary
    #             ( _Marker_key, symbol, markerType )
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
    # prior to 2/10/1999 rpp:
    # - added addtional accessor methods: getInfoByKey(), getSymbols().
    # - made SID comparisons case-insensitive
    # 
    #######################################################################

    # CLASS CONSTANTS:
    MARKERPOS = 0		# tuple-position of marker key
    SYMBOLPOS = 1		# tuple-position of marker symbol

    # field names associated with these positions
    FLDLIST = [None, None]
    FLDLIST[MARKERPOS] = "_MARKER_KEY"
    FLDLIST[SYMBOLPOS] = "SYMBOL"
    
    def __init__ ( self ):
	self._sids2Markers = {}
	self._markerInfo   = {}
	self._markers2sids = {}
	return


    def getInfoByKey ( self, mkey ):
	return self._markerInfo [ mkey ][:]


    def getMGIinfo ( self, sid, oneToOne=1, field=None ):
	#------------------------------------------------------------------
	# INPUTS:
	#    sid      : string -- Seq. ID for requesting marker info for.
	#    oneToOne : boolean -- whether only sids that associate with
	#                        a single marker should be returned.
	#    field    : string | None -- which field to return
	# OUTPUTS: List of ( Marker-Info Lists, or elements from this list )
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	# - Returns a reference to the desired list, instead of a copy;
	#   this is done strictly for performance reasons and the caller
	#   should not use the list reference to alter the contents of
	#   the list.
	#------------------------------------------------------------------
	_default = data = []
	sid = string.upper ( sid )
	if self._sids2Markers.has_key (sid):
	    data = self._sids2Markers[sid]
	    if oneToOne and len ( data ) > 1:
		data = _default
		
	    if field is not None:
		fldPos = None
		field = string.upper(field)
		if field in self.FLDLIST:
		    fldPos = self.FLDLIST.index ( field )
		else:
		    raise ValueError, " %s : field must be in %s." \
			  % ( __class__, str(self.FLDLIST)[1:-1] )
		d =[]
		for rec in data:
		    d.append ( rec [ fldPos ] )
		data = d
	return data


    def getMGIkeys ( self ):
	return self._markerInfo.keys()


    def getSIDkeys ( self ):
	return self._sids2Markers.keys()
    

    def getSIDsForMarker ( self, symbol, oneToOne = 0 ):
    #------------------------------------------------------------------
    # INPUTS:
    #   symbol : string
    #   oneToOne : boolean -- filter out sids that associate w/ multiple genes
    # OUTPUTS:
    #   List of SIDs (strings) | None:
    #       None -- if symbol not found in dictionary
    #       []   -- if oneToOne causes removal of all SIDs
    #       [sid,...] otherwise
    # ASSUMES: 	
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    #------------------------------------------------------------------
	results = None
	if self._markers2sids.has_key ( symbol ):
	    results = self._markers2sids [ symbol ]
	    if oneToOne:
		for sid in results[:]:
		    if len ( self._sids2markers[sid] ) > 1:
			results.remove (sid)
	return results
    

    def getSymbols ( self ):
	#------------------------------------------------------------------
	# INPUTS:
	# OUTPUTS: List of symbols for which we have SID-Marker Info
	# ASSUMES: 	
	# SIDE EFFECTS: 
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	results = self._markers2sids.keys()
	return results


    def length ( self ):
	return "SID keys %u" % len(self._sids2Markers)


    def load ( self, markerType ):
	#------------------------------------------------------------------
	# INPUTS:
	#    markerType : (markerType) or None
	# OUTPUTS: none
	# ASSUMES:
	# - That db.sql() can access needed environment variables in order
	#   to determine a default server/database.
	# SIDE EFFECTS: populates the class's primary, internal data members
	#               from the default MGD instance.
	# EXCEPTIONS: 
	# COMMENTS:
	#------------------------------------------------------------------

	# for significant marker info

	qryS = 'select sid = a.accID, m.symbol, m._Marker_key '
	qryF = 'from ACC_Accession a, MRK_Marker m '
	qryW = 'where a._MGIType_key = 2 ' + \
	       'and a._LogicalDB_key = %u ' % (SEQDB) + \
	       'and a._Object_key = m._Marker_key'

	if markerType:
	    qryF = qryF + ', MRK_Types t '
	    qryW = qryW + ' and m._Marker_Type_key = t._Marker_Type_key ' + \
		'and t.name = "%s" ' % (markerType)

	db.sql ( qryS + qryF + qryW, self.sidParser )
	
	return


    def sidParser ( self, row ):
	#------------------------------------------------------------------
	# INPUTS:  Dict -- SQL-tuple from query result set
	# OUTPUTS: none
	# ASSUMES:
 	# - query results contain expected columns
	#
	# SIDE EFFECTS: inserts/appends marker info to dict data member.
	# EXCEPTIONS: 
	# COMMENTS:  
	#------------------------------------------------------------------
	sid       = string.upper ( row["sid"] )
	markerKey = row["_Marker_key"]
	symbol    = row["symbol"]
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

	if self._markers2sids.has_key ( symbol ):
	    self._markers2sids[symbol].append (sid)
	else:
	    self._markers2sids[symbol] = [sid]
	    
	return

