## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: scorer.py,v 1.11 2007/07/24 17:30:45 vareille Exp $
#


import math
from math import sqrt
import numpy.oldnumeric as Numeric

from PyAutoDock.MolecularSystem import MolecularSystem


class ScoringStrategy:
    """Abstract class
    """
    def __init__(self, ms=None):
        pass
    
    def set_molecular_system(self, ms):
        """Abstract method
        """
        raise NotImplementedError, "abstract method"

    def get_score(self):
        """Abstract method
        """
        raise NotImplementedError, "abstract method"
    
# ScoringStrategy


class PairwiseScorer(ScoringStrategy):
    def __init__(self, ms=None):
        ScoringStrategy.__init__(self, None)
        if ms is not None:
            self.set_molecular_system(ms)
            
        self.required_attr_dictA = {}
        self.required_attr_dictB = {}


    def set_molecular_system(self, ms):
        """
ms, a MolecularSystem, manages which of its entity_sets is 'receptor'
and which 'ligand' via its configuration tuple and 
maintains the corresponding pairwise distance matrix. 

'set_molecular_system' checks that the currently designated entity_sets have
attributes required by this scorer class (required_attr_dicts
manage only checking a required attr once per entity_sets.)

@@FIX THIS: if change ms configuration, reset required_attr_dicts

"""
#        print "bases of ms", ms.__class__.__bases__
#        assert isinstance(ms, MolecularSystem)

        # check the required attribute for both subsets before going on
        listA = []
        for k,v in self.required_attr_dictA.items():
            if not v:
                listA.append(k)
                self.required_attr_dictA[k] = True
        ms.check_required_attributes( ms.configuration[0], listA)
        listB = []
        for k,v in self.required_attr_dictB.items():
            if not v:
                listB.append(k)
                self.required_attr_dictB[k] = True
        ms.check_required_attributes( ms.configuration[1], listB)

        # now set the molecular system
        self.ms = ms

    def _f(self, at_a, at_b):
        pass


    def get_score(self):
        if self.ms is None:
            raise RuntimeError("no molecular system available in scorer")
        array = self.get_score_array()
        return Numeric.add.reduce(Numeric.add.reduce(array))


    def get_score_array(self):
        """return pairwise score
        """
        # construct 2D array
        array = []
        for at_a in self.ms.get_entities(self.ms.configuration[0]):
            array.append([]) # a new row for every entity in first set
            row = array[-1]
            for at_b in  self.ms.get_entities(self.ms.configuration[1]):
                atom_score = self._f(at_a, at_b)
                row.append(atom_score)
        self.array = Numeric.array(array)
        self.post_process()
        return self.array

    def post_process(self):
        pass
# PairwiseScorer



class DistDepPairwiseScorer(PairwiseScorer):
    non_bonded_cutoff = 8.0 # Angstroms
        
    def __init__(self, ms=None):
        """constructor
        """
        PairwiseScorer.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('coords', False)
        self.required_attr_dictB.setdefault('coords', False)
        if ms is not None:
            self.set_molecular_system(ms)

        self.use_non_bond_cutoff = True


    def _f(self, at_a, at_b, dist):
        """distDepPairwise function stub
        """
        return 1.0


    def get_score_array(self):
        """return DistDepPairwise score
        """
        entity_ix = self.ms.configuration[0]
        entity_jx = self.ms.configuration[1]
        distance = self.ms.get_dist_mat(entity_ix, entity_jx)
        
        # construct 2D array
        array = []
        cut = self.non_bonded_cutoff
        if self.use_non_bond_cutoff==True:
            for ax, at_a in  enumerate(self.ms.get_entities(entity_ix)):
                array.append([]) # a new row for every entity in first set
                row = array[ax]  # the 
                for bx, at_b in  enumerate(self.ms.get_entities(entity_jx)):
                    d = distance[ax][bx]
                    atom_score = 0.0
                    # Obey non-bonded distance cutoff
                    if (d < cut):
                        atom_score = self._f(at_a, at_b, d)
                    row.append(atom_score)
        else: # no cut_off
            for ax, at_a in  enumerate(self.ms.get_entities(entity_ix)):
                array.append([]) # a new row for every entity in first set
                row = array[ax]  # the
                for bx, at_b in  enumerate(self.ms.get_entities(entity_jx)):
                    atom_score = self._f(at_a, at_b, distance[ax][bx] )
                    row.append(atom_score)
        self.array = Numeric.array(array)
        self.post_process()
        return self.array
# DistDepPairwiseScorer



class WeightedMultiTerm(DistDepPairwiseScorer):
    def __init__(self):
        DistDepPairwiseScorer.__init__(self)
        self.terms = []


    def set_molecular_system(self, ms):
        """
ms, a MolecularSystem, manages which of its entity_sets is 'receptor'
and which 'ligand' via its configuration tuple and 
maintains the corresponding pairwise distance matrix. 

'set_molecular_system' checks that the currently designated entity_sets have
attributes required by this scorer class. (required_attr_dicts
manage only checking a required attr once per entity_sets.)

@@FIX THIS: if change ms configuration, reset required_attr_dicts

"""
        # this call allows you to set the ms before any terms
        # are added. when terms are added (see add_term) set_molecular_system
        # will be called then.
        DistDepPairwiseScorer.set_molecular_system(self, ms)
        
        self.use_non_bond_cutoff = True
        for term in self.terms:
            term[0].set_molecular_system(self.ms)


    def add_term(self, term, weight=1.0):
        """add the term and weight as a tuple to the list of terms.
        """
        if hasattr(self, 'ms'):
            term.set_molecular_system(self.ms)
        self.terms.append( (term, weight) )


    def get_score(self):
        score = 0.0
        for term, weight in self.terms:
            score = score + weight*term.get_score()
        return score


    def get_score_per_term(self):
        scorelist = []
        for term, weight in self.terms:
            scorelist.append( weight*term.get_score() )
        return scorelist


    def get_score_array(self):
        #weightedMultiTerm
        t = self.terms[0]
        # do you really want the list of arrays ? or a list of number for each
        # scoring object?
        array = t[0].get_score_array() * t[1]
        if len(self.terms) > 1:
            for term, weight in self.terms[1:]:
                array = array + weight*term.get_score_array()
        self.array = array
        return self.array
# WeightedMultiTerm



class Distance(PairwiseScorer):
    """reference implementation of the Distance class
    """
    def __init__(self, ms=None):
        PairwiseScorer.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('coords', False)
        self.required_attr_dictB.setdefault('coords', False)
        if ms is not None:
            self.set_molecular_system(ms)


    #def _distance(self, a1, a2):
    def _f(self, at_a, at_b):
        a1 = at_a.coords
        a2 = at_b.coords
        return math.sqrt( (a2[0]-a1[0])**2 +
                          (a2[1]-a1[1])**2 +
                          (a2[2]-a1[2])**2)
# Distance



class HBondVDWSmoothing:
    def __init__(self, smooth_width=0.25):
        # Autodock smooth default is 0.5 which is then
        # divided by 2. before it's used
        self.set_smooth_width(smooth_width)


    def set_smooth_width(self, smooth_width):
        self.smooth_width = smooth_width # Angstoms


    def smooth_dist(self, dist, Rij,):
        """Adjust atomic distance to effectively broaden energy well

        dist is the distance between atoms
        Rij is the distance at the energy well minimum

        This implementation assumes that the energy function is
        monotonicly decreasing between 0 and Rij and monotonicly
        increasing for domain values greater than Rij
        """
        width = self.smooth_width # amount to broaden energy well

        # if dist is inside the "repulsive" side of the well
        if dist < (Rij-width):
            # move closer to energy well minimum
            new_dist = dist + width
            return new_dist
        
        # if dist is beyond the "attractive" side of the well
        if dist > (Rij + width):
            # move closer to energy well minimum
            new_dist = dist - width
            return new_dist

        # now dist is with-in width of Rij
        return Rij

    



if __name__ == '__main__':
    print "Tests are in Tests/test_scorer.py"
    # test_scorer.run_test()
