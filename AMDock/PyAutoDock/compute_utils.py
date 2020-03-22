##
## Copyright (C) The Scripps Research Institute 2006
##
## Authors: Alexandre Gillet <gillet@scripps.edu>
##  
## $Header: /opt/cvs/PyAutoDock/compute_utils.py,v 1.4 2007/10/10 22:15:41 vareille Exp $
## $Id: compute_utils.py,v 1.4 2007/10/10 22:15:41 vareille Exp $
##  
##


## utility functions used for computation 

import math
from MolKit.pdbWriter import PdbWriter
from MolKit.chargeCalculator import KollmanChargeCalculator,GasteigerChargeCalculator

from PyAutoDock.MolecularSystem import MolecularSystem
from PyAutoDock.AutoDockScorer import AutoDock305Scorer, AutoDock4Scorer
from PyAutoDock.AutoDockScorer import AutoDockTermWeights305, AutoDockTermWeights4
from PyAutoDock.trilinterp_scorer import TrilinterpScorer
from PyAutoDock.scorer import WeightedMultiTerm
from PyAutoDock.electrostatics import Electrostatics
from PyAutoDock.vanDerWaals import VanDerWaals,HydrogenBonding
from PyAutoDock.vanDerWaals import HydrogenBonding
from PyAutoDock.desolvation import Desolvation


import warnings

class EnergyScorer:
    """ Base class for energy scorer """

    def __init__(self,atomset1,atomset2,func=None):

        self.atomset1 =atomset1
        self.atomset2 =atomset2
        
        # save molecule instance of parent molecule
        self.mol1 = self.atomset1.top.uniq()[0]
        self.mol2 = self.atomset2.top.uniq()[0]
        # dictionary to save the state of each molecule when the
        # energy is calculated, will allow to retrieve the conformation
        # use for the energy calculation
        # keys are score,values is a list a 2 set of coords (mol1,mol2)
        self.confcoords = {}
        self.ms = ms = MolecularSystem()
        self.cutoff = 1.0
        self.score  = 0.0

                 
    def doit(self):

        self.update_coords()
        score,estat,hbond,vdw,ds= self.get_score()
        self.score = score
        self.saveCoords(score)
        self.atomset1.setConformation(0)
        self.atomset2.setConformation(0)
        return (score,estat,hbond,vdw,ds)

    def update_coords(self):
        """ methods to update the coordinate of the atoms set """
        pass

    def get_score(self):
        """ method to get the score """
        score = estat =  hbond = vdw = ds =  1000.
        return (score,estat,hbond,vdw,ds)


    def saveCoords(self,score):
        """methods to store each conformation coordinate.
         the score is use as the key of a dictionnary to store the different conformation.
         save the coords of the molecules to be use later to write out
         a pdb file
         We only save up 2 ten conformations per molecule. When 10 is reach we delete the one with the
         highest energy
         """
        score_int= int(score*100)
        # check number of conf save
        if len(self.confcoords.keys()) >= 50:
            # find highest energies
            val =max(self.confcoords.keys())
            del(self.confcoords[val])

        # add new conformation
        coords = [self.atomset1.coords[:],self.atomset2.coords[:]]
        self.confcoords[score_int] = coords


    def writeCoords(self,score=None,filename1=None,filename2=None,
                    sort=True, transformed=False,
                    pdbRec=['ATOM', 'HETATM', 'CONECT'],
                    bondOrigin='all', ssOrigin=None):
        """ write the coords of the molecules in pdb file
        pdb is file will have the molecule name follow by number of conformation
        """
        writer = PdbWriter()
        if score is None:
            score = min( self.confcoords.keys())
        if not self.confcoords.has_key(float(score)): return

        c1 = self.confcoords[score][0]
        c2 = self.confcoords[score][1]

        if filename1 is None:
            filename1 = self.mol1.name + '_1.pdb'
        prev_conf = self.setCoords(self.atomset1,c1)
        
        writer.write(filename1, self.atomset1, sort=sort, records=pdbRec,
                     bondOrigin=bondOrigin, ssOrigin=ssOrigin)

        self.atomset1.setConformation(prev_conf)

        if filename2 is None:
            filename2 = self.mol2.name + '_1.pdb'
            
        prev_conf = self.setCoords(self.atomset2,c2)
        writer.write(filename2, self.atomset2, sort=sort, records=pdbRec,
                     bondOrigin=bondOrigin, ssOrigin=ssOrigin)
        self.atomset2.setConformation(prev_conf)
        

    def setCoords(self,atomset,coords):
        """ set the coords to a molecule """
        mol = atomset.top.uniq()[0]
        prev_conf = atomset.conformation[0]
        # number of conformations available
        confNum = len(atomset[0]._coords)
        if hasattr(mol, 'nrgCoordsIndex'):
            # uses the same conformation to store the transformed data
            atomset.updateCoords(coords, 
                                 mol.nrgCoordsIndex)
        else:
            # add new conformation to be written to file
            atomset.addConformation(coords)
            mol.nrgCoordsIndex = confNum
        atomset.setConformation( mol.nrgCoordsIndex )
        return prev_conf

    def free_memory(self):
        """ Method to free memory allocate by scorer
        Should be implemented """

        pass


    
class TrilinterpEnergyScorer(EnergyScorer):
    """ Scorer using the trilinterp method, base on autogrid  
    """

    def __init__(self,atomset1,atomset2,stem, atomtypes):
        """ stem ( string) and atomtypes (list of string)2 list specify filenames for maps """
        
        EnergyScorer.__init__(self,atomset1,atomset2)
        self.l = self.ms.add_entities(self.atomset2)
        
        scorer = self.scorer = TrilinterpScorer(stem, atomtypes)
        self.scorer.set_molecular_system(self.ms)
 
        self.grid_obj = None

    def set_grid_obj(self,grid_obj):
        self.grid_obj = grid_obj

    def update_coords(self, index='arconformationIndex'):
        """ update the coords """
        if hasattr(self.mol1, index):
            num = self.mol1.__dict__.get('index')
            self.atomset1.setConformation(num)
        confNum = 0
        if hasattr(self.mol2, index):
            num = self.mol1.__dict__.get('index')
            self.atomset2.setConformation(num)
            confNum = num

        # transform ligand coord with grid.mat_transfo_inv
        # put back the ligand in grid space
        if hasattr(self.grid_obj,'mat_transfo_inv'):
            M = self.grid_obj.mat_transfo_inv
            vt = []
            for pt in self.mol2.allAtoms.coords:
                ptx = (M[0][0]*pt[0]+M[0][1]*pt[1]+M[0][2]*pt[2]+M[0][3])
                pty = (M[1][0]*pt[0]+M[1][1]*pt[1]+M[1][2]*pt[2]+M[1][3])
                ptz = (M[2][0]*pt[0]+M[2][1]*pt[1]+M[2][2]*pt[2]+M[2][3])
                vt.append( (ptx, pty, ptz) ) 
            self.mol2.allAtoms.updateCoords(vt,ind=confNum)
        
    def get_score(self):
        score = self.scorer.get_score()
        estat = 0.0
        hbond = 0.0
        vdw   = 0.0
        ds    = 0.0

        return (score,estat,hbond,vdw,ds)
    

pep_aromList  = ['PHE_CD1', 'PHE_CG', 'PHE_CD2', 'PHE_CE1',\
              'PHE_CE2', 'PHE_CZ', 'TYR_CD1', 'TYR_CG', 'TYR_CD2', 'TYR_CE1',\
              'TYR_CE2', 'TYR_CZ', 'HIS_CD2', 'HIS_CE1', 'HIS_CG', 'TRP_CD1',\
              'TRP_CG', 'TRP_CD2', 'TRP_CE2', 'TRP_CZ2', 'TRP_CH2', 'TRP_CZ3',\
              'TRP_AE3', 'PHE_AD1', 'PHE_AG', 'PHE_AD2', 'PHE_AE1',\
              'PHE_AE2', 'PHE_AZ', 'TYR_AD1', 'TYR_AG', 'TYR_AD2', 'TYR_AE1',\
              'TYR_AE2', 'TYR_AZ', 'HIS_AD2', 'HIS_AE1', 'HIS_AG', 'TRP_AD1',\
              'TRP_AG', 'TRP_AD2', 'TRP_AE2', 'TRP_AZ2', 'TRP_AH2', 'TRP_AZ3',\
              'TRP_AE3']


class PyADCalcAD3Energies(EnergyScorer):
    """For each atom in one AtomSet, determine the autodock3 energy vs all the atoms in a second
    AtomSet
    """

    def __init__(self,atomset1,atomset2):
        """ """        
        EnergyScorer.__init__(self,atomset1,atomset2)
        self.weight = None
        self.weightLabel = None

        self.scorer = AutoDock305Scorer()
        self.prop = self.scorer.prop
        
        bothAts = atomset1 + atomset2
        for a in bothAts:
            if a.parent.type + '_' + a.name in pep_aromList:
                a.autodock_element=='A'
                a.AtSolPar = .1027
            elif a.autodock_element=='A':
                a.AtSolPar = .1027
            elif a.autodock_element=='C':
                a.AtSolPar = .6844
            else:
                a.AtSolPar = 0.0        


        self.r = self.ms.add_entities(atomset1) 
        self.l = self.ms.add_entities(atomset2) 
        self.scorer.set_molecular_system(self.ms)    
        

    def update_coords(self, index='arconformationIndex'):
        """ update the coords """
        if hasattr(self.mol1, index):
            num = self.mol1.__dict__.get('index')
            self.atomset1.setConformation(num)
        if hasattr(self.mol2, index):
            num = self.mol1.__dict__.get('index')
            self.atomset2.setConformation(num)
        for ind in (self.r, self.l):
            # clear distance matrix
            self.ms.clear_dist_mat(ind)

            
    def get_score(self):
            
        score = self.scorer.get_score()
        terms_score = []
        for t,w in self.scorer.terms:
            terms_score.append(w*t.get_score())

        estat = min(round(terms_score[0]),1000.)
        hbond = min(round(terms_score[1]),1000.)
        vdw   = min(round(terms_score[2]),1000.)
        ds    = min(round(terms_score[3]),1000.)

        # labels atoms
        score_array = self.scorer.get_score_array()
        self.scorer.labels_atoms_w_nrg(score_array)
        
        return (score,estat,hbond,vdw,ds)
    

class PyADCalcAD4Energies(EnergyScorer):
    """For each atom in one AtomSet, determine the autodock4 energy vs all the atoms
    in a second AtomSet
    """

    def __init__(self,atomset1,atomset2):
        """ """        
        EnergyScorer.__init__(self,atomset1,atomset2)
        self.weight = None
        self.weightLabel = None

        self.scorer = AutoDock4Scorer()
        self.prop = self.scorer.prop
        
        self.r = self.ms.add_entities(atomset1) 
        self.l = self.ms.add_entities(atomset2) 
        self.scorer.set_molecular_system(self.ms)    
        

    def update_coords(self, index='arconformationIndex'):
        """ update the coords """
        if hasattr(self.mol1, index):
            num = self.mol1.__dict__.get('index')
            self.atomset1.setConformation(num)
        if hasattr(self.mol2, index):
            num = self.mol1.__dict__.get('index')
            self.atomset2.setConformation(num)
        for ind in (self.r, self.l):
            # clear distance matrix
            self.ms.clear_dist_mat(ind)


    def get_score(self):
        score = self.scorer.get_score()
        terms_score = []
        for t,w in self.scorer.terms:
            terms_score.append(w*t.get_score())

        estat = min(round(terms_score[0]),1000.)
        hbond = min(round(terms_score[1]),1000.)
        vdw   = min(round(terms_score[2]),1000.)
        ds    = min(round(terms_score[3]),1000.)

        # labels atoms
        score_array = self.scorer.get_score_array()
        self.scorer.labels_atoms_w_nrg(score_array)
        
        return (score,estat,hbond,vdw,ds)



class PyPairWiseEnergyScorer(EnergyScorer):
    """For each atom in one AtomSet, determine the electrostatics energy vs all the atoms in a second
    AtomSet
    """

    def __init__(self,atomset1,atomset2,scorer_ad_type='305'):

        EnergyScorer.__init__(self,atomset1,atomset2)
        self.r = self.ms.add_entities(self.atomset1)
        self.l = self.ms.add_entities(self.atomset2)

        
        self.scorer = WeightedMultiTerm()
        self.scorer.set_molecular_system(self.ms)

        self.scorer_ad_type = scorer_ad_type
        if self.scorer_ad_type == '305':
            self.ESTAT_WEIGHT_AUTODOCK = 0.1146 # electrostatics
            self.HBOND_WEIGHT_AUTODOCK = 0.0656 # hydrogen bonding
            self.VDW_WEIGHT_AUTODOCK   = 0.1485 # van der waals
            self.DESOLV_WEIGHT_AUTODOCK= 0.1711 # desolvation

        # different terms to be use for score
        self.estat= Electrostatics(self.ms)
        self.scorer.add_term(self.estat, self.ESTAT_WEIGHT_AUTODOCK)

        self.hbond=HydrogenBonding(self.ms)
        self.scorer.add_term(self.hBond, self.HBOND_WEIGHT_AUTODOCK)

        self.vdw = VanDerWaals(self.ms)
        self.scorer.add_term(self.vdw, self.VDW_WEIGHT_AUTODOCK)

        self.ds= Desolvation(self.ms)            
        self.scorer.add_term(self.ds,self.DESOLV_WEIGHT_AUTODOCK)
        

    def update_coords(self, index='arconformationIndex'):
        """ update the coords """
        if hasattr(self.mol1, index):
            num = self.mol1.__dict__.get('index')
            self.atomset1.setConformation(num)
        if hasattr(self.mol2, index):
            num = self.mol1.__dict__.get('index')
            self.atomset2.setConformation(num)
        for ind in (self.r, self.l):
            # clear distance matrix
            self.ms.clear_dist_mat(ind)


    def get_score(self):
            
        score = self.scorer.get_score()
        estat = min(round(self.estat.get_score() * self.ESTAT_WEIGHT_AUTODOCK,2),1000.)
        hbond = min(round(self.hbond.get_score() * self.HBOND_WEIGHT_AUTODOCK,2),1000.)
        vdw   = min(round(self.vdw.get_score()   * self.VDW_WEIGHT_AUTODOCK,2),1000.)
        ds    = min(round(self.ds.get_score()    * self.DESOLV_WEIGHT_AUTODOCK,2),1000.)

        return (score,estat,hbond,vdw,ds)
