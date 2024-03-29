
"""
agelib.py - Utilities for handling Age values

05/30/2006	lec
        - removed "perintal" and "postnatal immature"

"""

import sys
import re
import locale
from locale import atof

def ageMinMax (age):
    """Returns tuple of ints (ageMin, ageMax) given an age string
    """
    #------------------------------------------------------------------
    # INPUTS:     age as string
    # OUTPUTS:     PYTHON-tuple of ints (min, max) for range specification
    # ASSUMES:     
    # SIDE EFFECTS: 
    # EXCEPTIONS: 
    # COMMENTS:  
    # - This code was copied and adapted from Lori's Strains.py script
    #   in the MGI1.0 migration.
    #   See Requirements document for full details
    #   http://kelso:4444/software/mgi1.0/age.html
    #------------------------------------------------------------------

    #
    # Convert age to 'ageMin' and 'ageMax' values
    #

    ageMin = None
    ageMax = None
    ageOK = 1

    if age in ['Not Specified', 'Not Applicable']:
        ageMin = -1.0
        ageMax = -1.0
    elif age == 'embryonic':
        ageMin = 0.0
        ageMax = 21.0
#    elif age == 'perinatal':
#	ageMin = 17.00
#	ageMax = 22.0
    elif age == 'postnatal':
        ageMin = 21.01
        ageMax = 1846.0
    elif age == 'postnatal newborn':
        ageMin = 21.01
        ageMax = 25.0
#    elif age == 'postnatal immature':
#	ageMin = 25.01
#	ageMax = 42.0
    elif age == 'postnatal adult':
        ageMin = 42.01
        ageMax = 1846.0
    else:
        age = re.sub('or ', ',', age)    # 2 or 3 ==> 2,3
        age = re.sub('and ', ',', age)    # 2 and 3 ==> 2,3
        age = re.sub('to ', '-', age)    # 2 to 3 ==> 2-3
#	age = re.sub('+', '', age)	# 2+ ==> 2

        # only split into 3 elements
        try:
            ages = str.split(age, ' ', 2)
            stem = ages[0]
            timeUnit = ages[1]
            timeRange = ages[2]

            #
            # format is 'embryonic day x,y,z...' ==> (min(x,y,z), max(x,y,z))
            # format is 'embryonic day x-y,z...' ==> (min(x,y,z), max(x,y,z))
            # format is 'embryonic day x,y-z...' ==> ditto (rpp)
            #
            if str.find(timeRange, ',') >= 0:
                times = str.split(timeRange, ',')

                for i in range(len(times)):
                    t = x = times[i]
                    if str.find(t, '-') >= 0:
                        [x, y] = str.split(t, '-')

                        # rpp: I added this to insure get min/max for
                        # patterns that end in: ,y-z
                        # discarding the z's would lose the
                        # max of each range, yielding y instead of z.
                        # add the other onto the tail end of list
                        times.append (atof(y))

                    # replace each element to it's float value
                    times[i] = atof(x)

                ageMin = min(times)
                ageMax = max(times)

            #
            # format is 'embryonic day x-y' ==> (x,y)
            #
            elif str.find(timeRange, '-') >= 0:
                [ageMin, ageMax] = str.split(timeRange, '-')
                
                ageMin = atof(ageMin)
                ageMax = atof(ageMax)

            #
            # format is 'embryonic day x' ==> (x,x)
            #
            else:
                ageMin = ageMax = atof(timeRange)

            try:
                if stem == 'postnatal':
                    if timeUnit == 'day':
                        ageMin = ageMin + 21.01
                        ageMax = ageMax + 21.01
                    elif timeUnit == 'week':
                        ageMin = ageMin * 7 + 21.01
                        ageMax = ageMax * 7 + 21.01
                    elif timeUnit == 'month':
                        ageMin = ageMin * 30 + 21.01
                        ageMax = ageMax * 30 + 21.01
                    elif timeUnit == 'year':
                        ageMin = ageMin * 365 + 21.01
                        ageMax = ageMax * 365 + 21.01
    
            except:
                ageOK = 0

        except:
            ageOK = 0

        if ageMin is None or ageMax is None:
            ageOK = 0

        if not ageOK:
                ageMin = -1.0
                ageMax = -1.0

    return (ageMin, ageMax)
