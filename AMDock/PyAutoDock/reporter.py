## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

#
# Last modified on Fri May 20 18:42:34 PDT 2005 by lindy
#
# $Id: reporter.py,v 1.7 2007/07/24 17:30:45 vareille Exp $
#


import math
import numpy.oldnumeric as Numeric
import string
from MolKit.protein import Chain, Residue
from MolKit.molecule import Molecule, Atom


class Reporter:

    def __init__(self, scorer, level, config=0, sort=True):
        self.score_array = scorer.get_score_array()
        self.level = level
        #configuration is from the scorer's ms
        #NB if config is configuration[1], slicing is incorrect
        self.config = config
        self.entities = scorer.ms.get_entities(self.config).findType(self.level).uniq()
        #this may not be necessary
        if sort:
            self.entities.sort()
        

    def get_score_array(self):
        result = []
        index = 0 
        allAtoms = self.entities.findType(Atom)
        for e in self.entities:
            # slice the Numeric array
            entity_score = 0
            atoms = e.findType(Atom)
            for a in atoms:
                index = allAtoms.index(a)
                a_slice = self.score_array[index,:]
                entity_score+=Numeric.add.reduce(a_slice)
            # now sum the atom energies for this entity_slice
            result.append(entity_score)
        return result


    def get_score_array_unsafe(self):
        #this is unsafe because it relies on the atoms
        #being listed in same order as the entities..
        #eg if level is Residue, allAtoms in self.subset
        #are ordered so that all the atoms of residue1
        #preceed all the atoms of residue2 etc
        result = []
        index = 0 
        for e in self.entities:
            # slice the Numeric array
            num_atoms = len(e.findType(Atom))
            entity_slice = self.score_array[ index : index+num_atoms, :]
            index = index + num_atoms

            # now sum the atom energies for this entity_slice
            result.append(Numeric.add.reduce(
                Numeric.add.reduce( entity_slice)))
        return result


    def sanity_check(self):
        result1 = self.get_score_array()
        result2 = self.get_score_array_unsafe()
        errors = []
        for i in range(len(self.entities)):
            if abs(result1[i] - result2[i])>.000000001: 
                errors.append(i)
        if len(errors)==0:
            return 'pass'
        else:
            print 'indices differ:'
            return errors


    def pretty_print(self):
        print
        sa = self.get_score_array()
        for (ent, score) in zip(self.entities, sa):
            print "%s:\t% 8.4f" % (ent.full_name(), score)
            

    def write(self, fileptr):
        sa = self.get_score_array()
        for (ent, score) in zip(self.entities, sa):
            ostr = "%s:\t% 8.4f\n" % (ent.full_name(), score)
            fileptr.write(ostr)
            


class PerAtomTypeReporter:
    """ this reporter gets score_array per term, multiplies by weight, then
    reports av, max and min of all entries per atom type in the ligand"""

    def __init__(self, scorer, level=Atom, config=1, term_labels=['ele','hb', 'vdw', 'hph']):
        #config=1 makes self.entities all the ligand atoms, assuming they
        #were added second
        #configuration is from the scorer's ms
        #NB if config is configuration[1], slicing is incorrect
        self.config = config
        self.level = level
        self.entities = scorer.ms.get_entities(self.config)
        self.terms = scorer.terms
        self.term_labels = term_labels
        #build a list of atomtypes in this ligand, eg ['C','A','N','O','H']
        d = {}
        for e in self.entities: 
            d[e.autodock_element] = 1
        self.atomtypes = d.keys() 
        self.atomtypes.sort()  #sorted autodock_elements
        print "self.atomtypes=", self.atomtypes
        #SETUP list to hold one result dictionary for EACH TERM:
        self.stats = []


    def build_stats(self):
        ct = 0
        for t, w in self.terms:
            # dict to hold atomtype information per term: 
            # dict[tp]  a dictionary for each atom type
            dict = {}
            #initialize atomtype dictionaries for processing scorearray
            for tp in self.atomtypes:
                dict[tp] = []
                # keep of list of energies for each atomtype 
                # term + number of atoms 
            score_array = w * t.get_score_array()
            #print "0:score_array.shape", score_array.shape
            if ct==1:
                self.process_score_array(score_array, dict, ct)
            else:
                self.process_score_array(score_array, dict)
            self.stats.append(dict)
            ct+=1
        return self.stats


    #need to do this for each energy term
    def process_score_array(self, score_array, dict, verbose=0):
        #IS THERE A FASTER WAY TO DO THIS?
        #loop over all the atoms, building up numbers by element
        #print "1:score_array.shape", score_array.shape
        for ix, atm in enumerate(self.entities):
            #print ix,':', atm.name, '-', atm.autodock_element
            dict[atm.autodock_element].append(Numeric.add.reduce(score_array[:,ix][:]))

        #calc average, find min and max for this atom type
        #record in type_scores, type_maxs and type_mins dictionaries
        #for tp in self.atomtypes:
        #    d = dict[tp]
        #    type_scores = d['type_scores'][:]
        #    d['average'] = (Numeric.add.reduce(type_scores))/d['ctr']
        #    d['max'] =  max(type_scores)
        #    d['min'] = min(type_scores)

#sample output format from hsg1_ind: estat,hb,vdw,dsolv
#Ele:	 A  0.006  0.046 -0.001  C -0.040  0.000 -0.129  H -0.203 -0.024 -0.569  N  0.026  0.173 -0.232  O  0.208  0.737 -0.003 
#Hyd:	 A  0.000  0.000  0.000  C  0.000  0.000  0.000  H -0.296 -0.003 -0.489  N -0.078 -0.000 -0.388  O -0.069 -0.001 -0.269 
#Van:	 A -0.355 -0.182 -0.574  C -0.362 -0.274 -0.462  H -0.031 -0.020 -0.048  N -0.217 -0.180 -0.237  O -0.334 -0.224 -0.445 
#Des:	 A -0.016 -0.008 -0.025  C -0.115 -0.097 -0.140  H  0.118  0.118  0.118  N  0.000  0.000  0.000  O  0.236  0.236  0.236 

    def pretty_print(self):
        print
        #stats has keys of terms in scorer
        #currently no ligand has more than 6 atom types (?)
        for lab, dict in zip(self.term_labels, self.stats):
            print "% 3s:" % lab
            ctr = 0
            for tp in self.atomtypes:
                ll = dict[tp]
                av = Numeric.add.reduce(ll)/len(ll)
                mx = max(ll)
                mn = min(ll)
                print " % 2s % 6.3f % 6.3f % 6.3f "%(tp, av, mx, mn)
                ctr += 1
                if ctr==3:
                    print "\n\t"
                    ctr = 0
            print "\n"


    def write(self, fileptr):
        #for term, weight in self.terms:
        for lab, dict in zip(self.term_labels, self.stats):
            ostr =  "% 3s:" %lab
            ctr = 0
            for tp in self.atomtypes:
                ll = dict[tp]
                av = Numeric.add.reduce(ll)/len(ll)
                mx = max(ll)
                mn = min(ll)
                ostr = ostr + " % 2s % 6.3f % 6.3f % 6.3f "%(tp, av, mx, mn)
                ctr += 1
                if ctr==3:
                    ostr = ostr + "\n\t"
                    fileptr.write(ostr)
                    ostr = ""
                    ctr = 0
            ostr = ostr +  "\n"
            fileptr.write(ostr)
            


    

    
##################################################################

# UNIT TESTS

##################################################################


import unittest
from PyAutoDock.AutoDockScorer import AutoDock305Scorer
from MolecularSystem import MolecularSystem
from MolKit import Read


class ReporterTest(unittest.TestCase):
    
    err_epsilon = 0.000001
    def assertFloatEquals(self, float1, float2, digits=None):
        if digits is not None:
            float1 = round(float1, digits)
            float2 = round(float2, digits)
        difference = abs(float2 - float1)
        if difference == 0.0:
            self.assertEquals(float1, float2)
        else:
            try:
                eps = abs((float1/float2) - 1.0)
            except ZeroDivisionError:
                eps = abs((float2/float1) - 1.0)
            self.assertEquals((eps < self.err_epsilon), True,
                              msg="%f != %f; eps=%f" % (float1, float2, eps))
    # 1 method, 2 names
    assertFloatEqual = assertFloatEquals

    
    def setup_hsg1_ind(self):
        self.hsg1 = Read('Tests/Data/hsg1.pdbqs')
        self.hsg1[0].buildBondsByDistance()
        self.ind = Read('Tests/Data/docked_ind.pdbq')
        self.ms = MolecularSystem(self.hsg1.allAtoms)
        self.ms.add_entities(self.ind.allAtoms)

# ScorerTest



class Reporter_HSG1_ind_Test(ReporterTest):
    def setUp(self):
        # setup MolecularSystem
        self.setup_hsg1_ind() # defines self.ms, self.hsg1, self.ind
        
        # setup Scorer and get the (atom-atom) score_array
        self.ads = AutoDock305Scorer()
        self.ads.set_molecular_system(self.ms)
        #self.score_array = self.ads.get_score_array()
        # now were ready to hand off to the tests
        

    def tearDown(self):
        pass



class ReporterResidueTest(Reporter_HSG1_ind_Test):


    def test_hsg1_residues_01(self):
        # setup
        rr = Reporter(self.ads, Residue)
        
        # process
        residue_list = rr.get_score_array()
        
        # check
        # len of residue list = # of residues in subsetA
        self.assertEquals( len(residue_list),
                           len(self.hsg1.chains.residues))
        
        # sum of residue list = self.ads.get_score()
        self.assertFloatEquals(
            Numeric.add.reduce( residue_list),
            self.ads.get_score())

        rr.pretty_print()



class ReporterChainTest(Reporter_HSG1_ind_Test):



    def test_hsg1_chains_01(self):
        # setup
        cr = Reporter(self.ads, Chain)
        
        # process
        chain_list = cr.get_score_array()
        
        # check
        # len of chain list = # of chains in subsetA
        self.assertEquals( len(chain_list),
                           len(self.hsg1.chains))
        
        # sum of chain list = self.ads.get_score()
        self.assertFloatEquals(
            Numeric.add.reduce( chain_list),
            self.ads.get_score())

        cr.pretty_print()


class PerAtomTypeReporterTest(Reporter_HSG1_ind_Test):


    def test_hsg1_chains_01(self):
        # setup
        pATR = PerAtomTypeReporter(self.ads, Atom)
        # process
        stats = pATR.build_stats()
        # check
        # one dict entry for each term in scorer
        self.assertEquals( len(stats),
                           len(self.ads.terms))
        # each dict entry has correct number of types, ctr==5 
        # each dict entry has 49 entries total in score_lists
        for dict in stats:
            self.assertEquals( len(dict['A']),17)
            self.assertEquals( len(dict['C']),19)
            self.assertEquals( len(dict['H']),4)
            self.assertEquals( len(dict['N']),5)
            self.assertEquals( len(dict['O']),4)
        #pATR.pretty_print()
        test_output = open('test_output', 'w')
        pATR.write(test_output)
        test_output.close()

#test_output:
#ele:  A  0.006  0.046 -0.001   C -0.040  0.000 -0.129   H -0.203 -0.024 -0.569 
#	   N  0.026  0.173 -0.232   O  0.208  0.737 -0.003 
# hb:  A  0.000  0.000  0.000   C  0.000  0.000  0.000   H -0.296 -0.003 -0.489 
#	   N -0.078 -0.000 -0.388   O -0.069 -0.001 -0.269 
#vdw:  A -0.355 -0.182 -0.574   C -0.362 -0.274 -0.462   H -0.031 -0.020 -0.048 
#	   N -0.217 -0.180 -0.237   O -0.334 -0.224 -0.445 
#hph:  A -0.016 -0.008 -0.025   C -0.115 -0.097 -0.140   H  0.118  0.118  0.118 
#	   N  0.000  0.000  0.000   O  0.236  0.236  0.236


if __name__ == '__main__':

    test_cases = [
        'ReporterResidueTest',
        'ReporterChainTest',
        'PerAtomTypeReporterTest',
        ]
    
    unittest.main( argv=([__name__ ,'-v'] + test_cases) )

