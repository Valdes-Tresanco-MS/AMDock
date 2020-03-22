## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

#
# $Id: InternalEnergy.py,v 1.10 2007/07/24 17:30:45 vareille Exp $
#

import numpy.oldnumeric as Numeric
from MolKit.molecule import Atom
from PyAutoDock.MolecularSystem import MolecularSystem

from PyAutoDock.scorer import WeightedMultiTerm

from PyAutoDock.vanDerWaals import VanDerWaals, NewVanDerWaals
from PyAutoDock.vanDerWaals import HydrogenBonding
from PyAutoDock.vanDerWaals import NewHydrogenBonding, NewHydrogenBonding12_10

from PyAutoDock.electrostatics import Electrostatics 
from PyAutoDock.desolvation import NewDesolvation, Desolvation


class InternalEnergy(WeightedMultiTerm):
    """
    
    TODO:
      * sort out how the ms should be configured for internal energy.
        Should the ie_scorer get its own ms, or should a single ms
        be configured for a AutoDockScorer and then reconfigured for
        internal energy.
      * Unittest need independent/validated data.
      * there a 4x nested loop down in get_bonded_matrix
    """

    def __init__(self, exclude_one_four=False, weed_bonds=False):
        WeightedMultiTerm.__init__(self)
        self.exclude_one_four = exclude_one_four
        self.weed_bonds = weed_bonds


    def add_term(self, term, weight=1.0, symmetric=True):
        """add the term and weight as a tuple to the list of terms.
        """
        term.symmetric = symmetric
        if hasattr(self, 'ms'):
            term.set_molecular_system(self.ms)
        self.terms.append( (term, weight) )


    def print_intramolecular_energy_analysis(self, filename=None):
        """
        NOTE:For use ONLY with (autodock-like) 4 term scorers
        """
        num_atoms = len(self.ms.get_entities(0))
        ctr = 1
        dbm = self.get_diagonal_bonded_matrix(self.get_bonded_matrix())
        elec_sa = self.terms[0][0].get_score_array()*self.terms[0][1]*dbm
        vdw_sa = self.terms[1][0].get_score_array()*self.terms[1][1]*dbm
        hb_sa = self.terms[2][0].get_score_array()*self.terms[2][1]*dbm
        dsolv_sa = self.terms[3][0].get_score_array()*self.terms[3][1]*dbm
        dist_a = self.ms.get_dist_mat(0,0)
        if filename is not None:
            fptr = open(filename, 'w')
        for i in range(num_atoms):
            for j in range(i+1, num_atoms):
                if dbm[i][j]==0: continue
                elec = round(elec_sa[i][j],4)
                vdw = round(vdw_sa[i][j],4)
                hb = round(hb_sa[i][j],4)
                dsolv = round(dsolv_sa[i][j],4)
                dist = round(dist_a[i][j],2)
                tot = elec + vdw + hb + dsolv
                vdwhb = vdw + hb
                ostr = "%d     % 2d-%2d       % 6.2f    % +7.4f    % +6.4f   % +6.4f     % +6.4f" %(ctr,i+1,j+1,dist, tot,elec,vdwhb,dsolv)
                print ostr
                if filename:
                    ostr += '\n'
                    fptr.write(ostr)
                ctr += 1
        if filename: 
            fptr.close()



    def get_score_array(self):
        bonded_matrix = self.get_bonded_matrix()
        #score_array = WeightedMultiTerm.get_score_array(self)
        diagonal_bonded_matrix = self.get_diagonal_bonded_matrix(bonded_matrix)
        mask = diagonal_bonded_matrix
        #have to get each score_array and apply appropriate mask
        t = self.terms[0]
        if t[0].symmetric is False:
            mask = bonded_matrix
        array = t[0].get_score_array() * t[1] * mask
        if len(self.terms)>1:
            for term, weight in self.terms[1:]:
                mask = diagonal_bonded_matrix
                if term.symmetric is False:
                    mask = bonded_matrix
                array = array + term.get_score_array() * weight * mask
        #return score_array which is already filtered by bonded_matrix
        return array


    def get_score_per_term(self):
        bonded_matrix = self.get_bonded_matrix()
        diagonal_bonded_matrix = self.get_diagonal_bonded_matrix(bonded_matrix)
        scorelist = []
        for term, weight in self.terms:
            mask = diagonal_bonded_matrix
            if term.symmetric is False:
                mask = bonded_matrix
            #scorelist.append( weight*term.get_score() )
            #term_array = weight*term.get_score_array()*bonded_matrix
            term_array = weight*term.get_score_array()*mask
            scorelist.append(Numeric.add.reduce(Numeric.add.reduce(term_array)))
        return scorelist


    def get_score(self):
        return Numeric.add.reduce(Numeric.add.reduce(self.get_score_array()))


    def get_diagonal_bonded_matrix(self, mask):
        #make it zero on and below the diagonal
        for i in range(len(mask[0])):
            for j in range(0, i):
                mask[i][j] = 0
        return mask
        

    def get_bonded_matrix(self, entities=None):
        """return array of floats 1. means non-bonded, 0. means bonded

        bonded means 1-1, 1-2, or 1-3
        """
        if entities is None:
            entities = self.ms.get_entities(self.ms.configuration[0])

        atoms = entities.findType(Atom)
        lenAts = len(atoms)

        # initialize an lenAts-by-lenAts array of False
        #mat = [[False]*lenAts]*lenAts
        mask = Numeric.ones((lenAts, lenAts), 'f')

        for a1 in atoms:
            # mark 1-1 interactions (yourself)
            ind1 = atoms.index(a1)
            mask[ind1,ind1] = 0.

            # mark 1-2 interactions (your one-bond neighbors)
            for b in a1.bonds:
                a2 = b.atom1
                if id(a2)==id(a1):
                    a2 = b.atom2
                ind2 = atoms.index(a2)
                mask[ind1,ind2] = 0.
                mask[ind2,ind1] = 0.

                # mark 1-3 interactions (your neighbors' neighbors)
                for b2 in a2.bonds:
                    a3 = b2.atom1
                    if id(a3)==id(a2): a3 = b2.atom2
                    if id(a3)==id(a1): continue
                    ind3 = atoms.index(a3)
                    mask[ind1,ind3] = 0.
                    mask[ind3,ind1] = 0.
                    if self.exclude_one_four:
                        for b3 in a3.bonds:
                            a4 = b3.atom1
                            if id(a4)==id(a3): 
                                a4 = b3.atom2
                            if id(a4)==id(a2): continue
                            if id(a4)==id(a1): continue
                            ind4 = atoms.index(a4)
                            mask[ind1,ind4] = 0.
                            mask[ind4,ind1] = 0.

        if self.weed_bonds:
            mask = self.weedbonds(mask)

        return mask



    def weedbonds(self, mask):
        #mask = self.get_bonded_matrix(entities)
        entities = self.ms.get_entities(self.ms.configuration[0])
        atoms = entities.findType(Atom)
        lenAts = len(atoms)
        mols = atoms.top.uniq()
        for m in mols:
            if not hasattr(m, 'torTree'):
                continue
            l = []
            atL = m.torTree.rootNode.atomList
            #print 'setting 0 for rootNode atomList:', atL
            for i in atL:
                for j in atL:
                    mask[i][j] = 0
            for n in m.torTree.torsionMap:
                atL = n.atomList[:]
                atL.extend(n.bond)
                #print 'setting 0 for atomList:', atL
                for i in atL:
                    for j in atL:
                        mask[i][j] = 0
            print
        return mask


    def print_mask(self, mask):
        I, J = mask.shape
        for i in range(I):
            for j in range(J):
                print int(mask[i][j]),
            print




####
#### Unittests (to be moved away later)
####

###import unittest
###from PyAutoDock.Tests.test_scorer import ScorerTest
###from MolKit import Read

###class InternalEnergyTest(ScorerTest):
###    def setUp(self):
###        pass
###    def tearDown(self):
###        pass

###    def test_d1_new(self):
###        """InternalEnergy refactored to subclass WeightedMultiTerm
###        """
###        # create the MolecularSystem
###        filename = 'Tests/Data/d1.pdbqs'
###        d1 = Read(filename)
###        d1[0].buildBondsByDistance()

###        ms = MolecularSystem()
###        ms.add_entities(d1.allAtoms) # only add it once

###        # create the InternalEnergy term
###        iec = InternalEnergy()
###        iec.add_term( VanDerWaals(), 0.1485 )

###        # put the MolecularSystem and the scorer together
###        print "MS?", isinstance(ms, MolecularSystem)
###        iec.set_molecular_system(ms)
###        
###        score = iec.get_score()
###        score_array = iec.get_score_array()

###        #print "Internal Energy of %s: %14.10f\n" % (filename, score)
###        
###        #self.assertFloatEqual( score, 0.116998674, 4)
###        #3/23/2005: diagonal result is HALF of previous value
###        self.assertFloatEqual( score, 0.116998674/2.0, 4)


###    def test_d1_all_terms(self):
###        # create the MolecularSystem
###        filename = 'Tests/Data/d1.pdbqs'
###        d1 = Read(filename)
###        d1[0].buildBondsByDistance()

###        ms = MolecularSystem()
###        ms.add_entities(d1.allAtoms) # only add it once

###        # create the InternalEnergy term
###        iec = InternalEnergy()
###        iec.add_term( VanDerWaals(), 0.1485 )
###        iec.add_term( HydrogenBonding(), 0.0656, symmetric=False )
###        iec.add_term( Electrostatics(), 0.1146 )
###        iec.add_term( Desolvation(), 0.1711, symmetric=False )

###        # put the MolecularSystem and the scorer together
###        iec.set_molecular_system(ms)
###        
###        score = iec.get_score()
###        print "Internal Energy of %s: %14.10f\n" % (filename, score)
###        #score_array = iec.get_score_array()
###        score_list = iec.get_score_per_term()
###        print "VanDerWaals=", score_list[0]            
###        #self.assertFloatEqual( score_list[0], 0.117, 4)
###        #3/23/2005: diagonal result is HALF of previous value
###        self.assertFloatEqual( score_list[0], 0.117/2.0, 4)
###        #??hb was -0.2411... now is -0.2400....????
###        #self.assertFloatEqual( score_list[1],-0.2411, 4)
###        print "HydrogenBonding=", score_list[1]            
###        #3/23/2005: diagonal result is NOT HALF of previous value???
###        self.assertFloatEqual( score_list[1],-0.2400, 4)
###        print "Electrostatics=", score_list[2]            
###        #self.assertFloatEqual( score_list[2], 0.6260, 4)
###        #3/23/2005: diagonal result is HALF of previous value
###        self.assertFloatEqual( score_list[2], 0.6260/2., 4)
###        print "Desolvation=", score_list[3]            
###        #self.assertFloatEqual( score_list[3], 1.416, 4)
###        #3/23/2005: diagonal result is NOT HALF of previous value!!!
###        #BECAUSE AD3 DESOLVATION IS NOT SYMMETRIC!!!!
###        self.assertFloatEqual( score_list[3], 1.416, 4)
###        #3/23/2005: diagonal result is NOT HALF of previous value
###        #because HydrogenBonding and Desolvation were not..
###        #self.assertFloatEqual( score, 1.9179/2., 4)
###        newsum = 0.117/2. -0.2400 + .6260/2. + 1.416

###        self.assertFloatEqual( score, newsum, 4)


###    def test_d1_new_terms(self):
###        # create the MolecularSystem
###        filename = 'Tests/Data/d1.pdbqt'
###        filename = 'Tests/Data/piece_d1.pdbqt'
###        d1 = Read(filename)
###        d1[0].buildBondsByDistance()

###        ms = MolecularSystem()
###        ms.add_entities(d1.allAtoms) # only add it once

###        # create the InternalEnergy terms
###        iec = InternalEnergy(exclude_one_four=True)
###        iec.add_term( NewVanDerWaals(), 1. )
###        iec.add_term( NewHydrogenBonding12_10(), 1. ) #this is hydrogenbonding
###        #iec.add_term( NewHydrogenBonding(), 0.0656 )
###        iec.add_term( Electrostatics(), 0.0091 )
###        iec.add_term( NewDesolvation(), 0.0174 )

###        # put the MolecularSystem and the scorer togethern
###        iec.set_molecular_system(ms)
###        
###        score = iec.get_score()

###        # correct scores from
###        #score=0.0959013722
###        print "Internal Energy of %s: %14.10f\n" % (filename, score)

###        #score_array = iec.get_score_array()
###        score_list = iec.get_score_per_term()
###        #print "VanDerWaals=", score_list[0]            
###        #self.assertFloatEqual( score_list[0], 0.117, 4)
###        #print "HydrogenBonding=", score_list[1]            
###        #self.assertFloatEqual( score_list[1],-0.2411, 4)
###        #print "Electrostatics=", score_list[2]            
###        #self.assertFloatEqual( score_list[2], 0.6260, 4)
###        #print "Desolvation=", score_list[3]            
###        #self.assertFloatEqual( score_list[3], 1.416, 4)
###        #without the Desolvation term the total is 0.5019
###        #self.assertFloatEqual( score, 0.5019, 4)
###        #self.assertFloatEqual( score, 1.9179, 4)
###        #VanDerWaals= 0.0282212653592
###        #HydrogenBonding= -0.00653238892803
###        #Electrostatics= 0.0497082608073
###        #Desolvation= 0.0245042349353
###        print "NewVanDerWaals=", score_list[0]            
###        #self.assertFloatEqual( score_list[0], 0.117, 4)
###        print "NewHydrogenBonding12_10=", score_list[1]            
###        #self.assertFloatEqual( score_list[1],-0.2411, 4)
###        print "Electrostatics=", score_list[2]            
###        #self.assertFloatEqual( score_list[2], 0.6260, 4)
###        print "NewDesolvation=", score_list[3]            
###        #self.assertFloatEqual( score_list[3], 1.416, 4)

###    def test_piece_d1_new_terms(self):
###        # create the MolecularSystem
###        filename = 'Tests/Data/piece_d1.pdbqt'
###        d1 = Read(filename)
###        d1[0].buildBondsByDistance()

###        ms = MolecularSystem()
###        ms.add_entities(d1.allAtoms) # only add it once

###        # create the InternalEnergy terms
###        iec = InternalEnergy(exclude_one_four=True)
###        #iec.add_term( NewVanDerWaals(), 1. )
###        iec.add_term( NewVanDerWaals(), 1. )
###        iec.add_term( NewHydrogenBonding12_10(), 1. ) #this is hydrogenbonding
###        #iec.add_term( NewHydrogenBonding(), 0.0656 )
###        iec.add_term( Electrostatics(), 1. )
###        iec.add_term( NewDesolvation(), 1. )

###        # put the MolecularSystem and the scorer togethern
###        iec.set_molecular_system(ms)
###        
###        score = iec.get_score()
###        score_list = iec.get_score_per_term()
###        
###        # correct scores from @@ where are these from, again?? 
###        #ie_score = -0.4292339075
###        #vdw_score = -0.427359240096
###        #hbond_score = 0.0
###        #estat_score = -0.00255480130265
###        #dsolv_score = 0.0006801339114
###        #9/24 weightless scores:
###        ie_score = -2.66669923187     #changed 9/24
###        vdw_score = -2.7696645502     #changed 9/24
###        hbond_score = 0.0
###        estat_score = -0.280747395895 #changed 9/24
###        dsolv_score = 0.383712714226  #changed 9/24

###        #print "score_list="
###        #for ix, t in enumerate(score_list):
###            #print ix,':', t
###        #print " total=", Numeric.add.reduce(score_list)

###        # check (pre)-calculated and returned values...
###        #3/23/2005: diagonal results are HALF of previous values
###        self.assertAlmostEqual(vdw_score/2.0, score_list[0])
###        self.assertAlmostEqual(hbond_score/2.0, score_list[1])
###        self.assertAlmostEqual(estat_score/2.0, score_list[2])
###        self.assertAlmostEqual(dsolv_score/2.0, score_list[3])
###        self.assertAlmostEqual(ie_score/2.0, score)


###    def test_no_terms(self):
###        """InternalEnergy with no terms
###        """
###        # create the MolecularSystem
###        filename = 'Tests/Data/d1.pdbqs'
###        d1 = Read(filename)[0]
###        d1.buildBondsByDistance()

###        ms = MolecularSystem()
###        ms.add_entities(d1.allAtoms)
###        ms.add_entities(d1.allAtoms)
###        
###        # create the InternalEnergy term
###        iec = InternalEnergy()
###        # self.add_term( VanDerWaals(), 0.1485 )

###        # put the MolecularSystem and the scorer togethern
###        iec.set_molecular_system(ms)
###        
###        self.assertRaises( IndexError, iec.get_score )


###if __name__ == '__main__':
###    unittest.main()
