############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2007
#
#############################################################################

#
# $Id: shaperecognition.py,v 1.1 2007/04/13 20:17:35 rhuey Exp $
#

import math
from scorer import ScoringStrategy
from mglutil.math import usr


class ShapeRecognitionRefImpl(ScoringStrategy):
    """reference implementation of the 

"""
    def __init__(self, ms=None):
        ScoringStrategy.__init__(self)
        if ms is not None:
            self.set_molecular_system(ms)


    def set_molecular_system(self, ms):
        self.ms = ms


    def get_score(self):
        """
        """
        usr0 = usr.usr_descriptors( self.ms.get_coords(0))
        usr1 = usr.usr_descriptors( self.ms.get_coords(1))
        return usr.usr_similarity( usr0, usr1)

ShapeRecognition = ShapeRecognitionRefImpl
# ShapeRecognitionRefImpl

if __name__ == '__main__':
    pass
    # test_scorer.run_test()
