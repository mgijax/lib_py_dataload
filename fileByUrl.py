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
    An importable module that supplies a wrapper class, URLFile, for
    urllib module's urlopen(). URLFile removes the header from the URL
    text stream and provides a FILE-like access interface to the data stream.

Syntax:
(Command Line -- writes to stdout:)
fileByUrl.py <myURL>  > <dest file name>

(Python:)
import fileByUrl
urlFile = fileByUrl.URLFile (<myURL>)

Options:
    
"""
############################################################################
# AUTHOR: R. Palazola
# DATE:   9/3/1999
# VERSION: %W%
#
# PURPOSE: see __doc__ string above
#---------------------------------------------------------------------------
# USAGE: see __doc__ string above
#
#---------------------------------------------------------------------------
# INPUT FORMAT: n/a
#
#---------------------------------------------------------------------------
# PROCESSING -- what it does with the input:
#
#---------------------------------------------------------------------------
# KNOWN DEFECTS:
# The header stripping logic is simplistic:
#   Text files that have initial lines with first word ending in ":" will
#   be stripped (incorrectly) as part of the header unless there is a leading
#   empty line.
#
#---------------------------------------------------------------------------
# NOTES:
# This class does not provide a read() method similar to objects returned by
# openUrl().
# The logic for stripping the header lines may be simplistic and need
# beefing-up to make reliable and prevent inadvertent stripping of
# initial lines with 1st word ending in ":"
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

import string, urllib

############
# MAIN:
#-----------

class URLFile:
    #######################################################################
    # DATA MEMBERS:
    #   url : String (URL address) or None
    #   fd  : urlopen()-returned FILE-like object
    #   __headStripped : boolean -- records state of stripping the http
    #                               stream's header record
    #
    # METHODS:
    #   __init__ ( [URL : string] )
    #   open ( URL : string )
    #   readline ()
    #   readlines()
    #   close()
    #   __del__ ()
    #
    # USEAGE:
    #   urlObj = URLFile ("http://....")
    #   contents = urlObj.readlines()
    #   urlObj.close()
    #
    # NOTES:
    #
    # ASSUMES:
    #
    # MODIFICATIONS:
    #######################################################################
    
    def __init__ (self,  url = None ):
	self.url = url
	self.fd = None
	self.__headerStripped = 0
	if url:
	    self.open (url)
	return

    def open ( self, url ):
	# may raise IOError if cannot open
	self.fd = urllib.urlopen ( url )
	self.__headerStripped = 0
	return

    def readline ( self ):
	if not self.fd:
	    raise IOError, "URLFile object not opened."
	
	line = self.fd.readline()
	while not self.__headerStripped and line:
	    # remove the urllib header record (1st words end in a colon)
	    words = string.split(line)
	    if words and words[0][-1] == ':' :
		line = self.fd.readline()
	    else:
		self.__headerStripped = 1
	    
	return line

    def close ( self ):
	if self.fd:
	    self.fd.close()
	    self.__headerStripped = 0
	return

    def __del__ ( self ):
	if self.fd:
	    self.fd.close()
	return

    def readlines ( self ):
	line = self.fd.readline()
	lines = []
	while line:
	    lines.append ( line[:-1] )
	    line = self.fd.readline()
	return lines

if __name__ == "__main__":
    import sys
    sys.stderr.write ( str(sys.argv) + "\n" )
    if len (sys.argv) <= 1:
	print __doc__
    else:
	url = sys.argv[1]
	urlFile = URLFile ( url )
	line = urlFile.readline()
	while line:
	    sys.stdout.write ( line )
	    sys.stdout.flush ()
	    line = urlFile.readline()
	urlFile.close()

