# Makefile for lib_py_misc
#
# PREFIXDIR is the macro that specifies the directory under which this 
# product will be installed, and thus is only meaningful for the 
# "install" target. For example, if PREFIXDIR is set to 
# "/usr/local/mgi/depot/productname", the resulting installation would be 
# in bin, lib, etc, man, and system_docs directories under 
# /usr/local/mgi/depot/productname/.
#
# Example:  make [target]  
#           or
#           make PREFIXDIR=<directoryname> install 
# 

SRCS= accessionLoadUtils.py BCPWrite.py fileByUrl.py unigeneLib.py

all:

install:
	# check prefix 
	@ if \
        [ ! -d ${PREFIXDIR} ] ; \
	then \
		echo "${PREFIXDIR} is not a directory" ; \
		exit 1 ; \
	fi

	# create the 'lib' directory under the prefix dir, if necessary 
	@ if \
        [ ! -d ${PREFIXDIR}/lib ] ; \
	then \
		mkdir ${PREFIXDIR}/lib ; \
	fi

	# copy files and set _default_ permissions:
	@ for f in ${SRCS} ; \
	do \
		echo $$f ; \
		cp -f $$f ${PREFIXDIR}/lib/ ; \
		chmod 444 ${PREFIXDIR}/lib/$$f ; \
	done
