## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: William Lindstrom, Ruth Huey , Alex Gillet
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: AutoDockScorer.py,v 1.24 2010/05/06 21:03:08 rhuey Exp $
#


import math
import numpy.oldnumeric as Numeric

from PyAutoDock.scorer import WeightedMultiTerm

from vanDerWaals import VanDerWaals, HydrogenBonding
from vanDerWaals import  NewHydrogenBonding, NewVanDerWaals
from desolvation import Desolvation
from desolvation import NewDesolvation, NewDesolvationLigOnly, NewDesolvationAtomMap
from electrostatics import Electrostatics


class AutoDockTermWeights305:
    def __init__(self):
        self.name = 'asdf'

    estat_weight = 0.1146 # Autogrid3 weight
    dsolv_weight = 0.1711 # Autogrid3 weight
    hbond_weight = 0.0656 # Autogrid3 weight
    vdw_weight = 0.1485 # Autogrid3 weight
# AutoDockTermWeights305


class AutoDockTermWeights4_1:
    def __init__(self):
      self.name = '9_28_2004'

    estat_weight = 0.1408 # .1146*1.229 
    dsolv_weight = 0.122 # 9/28/04 weight
    hbond_weight = 0.1267 #.0656*1.931
    vdw_weight   = 0.1488 #.1485*1.002
# AutoDockTermWeights4_1



class AutoDockTermWeights4_2:
    def __init__(self):
      self.name = '5_5_2005'

    vdw_weight   = 0.1570 # .1485*1.057
    hbond_weight = 0.1344 # .0656*2.048
    estat_weight = 0.1319 # .1146*1.151 
    dsolv_weight = 0.1350 # 5/5/05 weight
# AutoDockTermWeights4_2


class AutoDockTermWeights4:
    def __init__(self):
      self.name = '8_2005'

    vdw_weight   = 0.1560 # .1485*1.05037
    hbond_weight = 0.0974 # .0656*1.48452
    estat_weight = 0.1465 # .1146*1.27907 
    dsolv_weight = 0.1159 # 8/05 weight
    tors_weight  = 0.2744 #
# AutoDockTermWeights4


class AutoDockTermWeights41:
    def __init__(self):
      self.name = '9_2007'

    vdw_weight   = 0.1662 #
    hbond_weight = 0.1209 #
    estat_weight = 0.1406 #
    dsolv_weight = 0.1322 #
    tors_weight  = 0.2983 #
# AutoDockTermWeights41

        
class AutoGrid305Scorer(WeightedMultiTerm, AutoDockTermWeights305):
    """
A handy scorer for AutoGrid305 atom maps.

Note that the Electrostatics term does not contribute to the atom
maps but is in a map of its own (the .e.map).
"""
    def __init__(self):
        WeightedMultiTerm.__init__(self)
        AutoDockTermWeights305.__init__(self)
        self.add_term(HydrogenBonding(), self.hbond_weight)
        self.add_term(VanDerWaals(), self.vdw_weight)
        self.add_term(Desolvation(), self.dsolv_weight)
# AutoGrid305Scorer



class AutoDock305Scorer(WeightedMultiTerm, AutoDockTermWeights305):
    def __init__(self):
      self.prop = 'ad305_energy'
      WeightedMultiTerm.__init__(self)
      AutoDockTermWeights305.__init__(self)
      self.add_term(Electrostatics(), self.estat_weight)
      self.add_term(HydrogenBonding(), self.hbond_weight)
      self.add_term(VanDerWaals(), self.vdw_weight)
      self.add_term(Desolvation(), self.dsolv_weight)
        

    def get_score_array(self):
      """ return a list of score for each terms per atoms"""
      # add up vdw, estat and hbond
      t = self.terms[0]
      # do you really want the list of arrays ? or a list of number for each
      # scoring object?
      array = t[0].get_score_array() * t[1]
      for term, weight in self.terms[1:]:
        array = array + weight*term.get_score_array()

      self.array = array
      return self.array
    

    def labels_atoms_w_nrg(self,score_array):
      """ will label each atoms with a nrg score """
      # label each first atom by sum of its ad3 interaction energies 
      firstAts = self.ms.get_entities(0)
      
      for i in range(len(firstAts)):
        a = firstAts[i]
        vdw_hb_estat_ds =Numeric.add.reduce(score_array[i])
        setattr(a, self.prop, vdw_hb_estat_ds)
        ## NOT sure we need the following anymore... ASK Ruth
##         vdw_hb_estat = Numeric.add.reduce(score_array[i])
##         if a.element=='O':
##           setattr(a, self.prop, .236+vdw_hb_estat)   #check this
##         elif a.element=='H':
##           setattr(a, self.prop, .118+vdw_hb_estat)   #check this
##         else:
##           setattr(a, self.prop, Numeric.add.reduce(self.dsolv_array[i])+vdw_hb_estat)

      # label each second atom by sum of its vdw interaction energies
      secondAts = self.ms.get_entities(1)
      swap_result = Numeric.swapaxes(score_array,0,1)
      for i in range(len(swap_result)):
          a = secondAts[i]
          vdw_hb_estat_ds =Numeric.add.reduce(swap_result[i])
          setattr(a, self.prop, vdw_hb_estat_ds)
                
##         vdw_hb_estat = Numeric.add.reduce(swap_result[i])
##         if a.element=='O':
##           setattr(a, self.prop, .236+vdw_hb_estat)   #check this
##         elif a.element=='H':
##           setattr(a, self.prop, .118+vdw_hb_estat)   #check this
##         else:
##           setattr(a, self.prop, Numeric.add.reduce(swap_dsolv[i])+vdw_hb_estat)

# AutoDock305Scorer


class AutoDock4Scorer(WeightedMultiTerm, AutoDockTermWeights4):
    def __init__(self):
        self.prop = 'ad4_energy'
        WeightedMultiTerm.__init__(self)
        AutoDockTermWeights4.__init__(self)
        self.add_term(Electrostatics(), self.estat_weight)    
        self.add_term(NewHydrogenBonding(), self.hbond_weight) 
        self.add_term(NewVanDerWaals(), self.vdw_weight)      #.1485*1.002
        self.add_term(NewDesolvation(), self.dsolv_weight) 


    def get_score_array(self):
        """ return a list of score for each terms per atoms"""
        # NEED TO CORRECT hbond
        # result = self.scorer.get_score_array()
        sal = score_array_list = []
        for t, w in self.terms:
            sal.append(t.get_score_array()*w)
        self.hbond_array = sal[1]
        result = Numeric.add(sal[0], sal[2])
        result = Numeric.add(result, sal[3])
        self.array = result
        return self.array


    def labels_atoms_w_nrg(self,score_array):
        """ will label each atoms with a nrg score """

        # label each first atom by sum of its vdw interaction energies 
        firstAts  = self.ms.get_entities(0)
        for i in range(len(firstAts)):
            # firstAts[i].vdw_energy = Numeric.add.reduce(score_array[i])
            hbond_val =  min(self.hbond_array[i])+max(self.hbond_array[i])
            setattr(firstAts[i], self.prop, Numeric.add.reduce(score_array[i])+hbond_val)
        # label each second atom by sum of its vdw interaction energies
        secondAts = self.ms.get_entities(1)
        swap_result = Numeric.swapaxes(score_array, 0,1)
        swap_hbond_array = Numeric.swapaxes(self.hbond_array, 0, 1)
        for i in range(len(swap_result)):
            #secondAts[i].vdw_energy = Numeric.add.reduce(swap_result[i])
            hbond_val =  min(swap_hbond_array[i])+max(swap_hbond_array[i])
            setattr(secondAts[i], self.prop, Numeric.add.reduce(swap_result[i])+hbond_val)      

# AutoDock4Scorer


class AutoDock4ScorerLigOnly(WeightedMultiTerm, AutoDockTermWeights4):
    def __init__(self):
        WeightedMultiTerm.__init__(self)
        self.add_term(Electrostatics(), self.estat_weight)    
        self.add_term(NewHydrogenBonding(), self.hbond_weight) 
        self.add_term(NewVanDerWaals(), self.vdw_weight)      #.1485*1.002
        self.add_term(NewDesolvationLigOnly(), self.dsolv_weight) 

# AutoDock4Scorer


class AutoDock4Scorer2(WeightedMultiTerm):
    #weights in the scorer for NewVanDerWaalsHybridWeights
    def __init__(self):
        WeightedMultiTerm.__init__(self)
        self.add_term(Electrostatics(), 0.1146)
        self.add_term(NewHydrogenBonding(), 0.1852)  #.0656*2.82292 = 0.1851836
        self.add_term(NewVanDerWaalsHybridWeights(), 1.0)   #varying weights in scorer
        self.add_term(NewDesolvation(), 1.0)         #.1711*0.10188 = 0.0174317
# AutoDock4Scorer2


class AutoDock41Scorer(WeightedMultiTerm, AutoDockTermWeights41):
    def __init__(self, exclude_torsFreeEnergy=False, verbose=False):
        self.verbose = verbose
        if verbose: print "initialized exclude_torsFreeEnergy=", exclude_torsFreeEnergy
        self.prop = 'ad41_energy'
        self.exclude_torsFreeEnergy=exclude_torsFreeEnergy
        WeightedMultiTerm.__init__(self)
        AutoDockTermWeights41.__init__(self)
        self.add_term(Electrostatics(), self.estat_weight)    
        self.add_term(NewHydrogenBonding(), self.hbond_weight) 
        self.add_term(NewVanDerWaals(), self.vdw_weight)   
        self.add_term(NewDesolvation(), self.dsolv_weight) 
        self.supported_types = self.get_supported_types()


    def get_supported_types(self):
        double_types = self.terms[2][0].epsij.keys()
        supported_types = []
        odd_length = []
        for t in double_types:
            if len(t)==4:
                supported_types.append(t[:2])
            elif len(t)==2:
                supported_types.append(t[0])
            elif len(t)==3:
                odd_length.append(t)
            else:
                raise "get_supported_types found badly formed autodock_element", t
        #check the 3-length autodock_elements [where did this come from??]
        for t in odd_length:
            t1 = t[:2]
            t2 = t[1:]
            ok = 0
            if t1 in supported_types and t[2] in supported_types:
                ok = 1
            if t2 in supported_types and t[0] in supported_types:
                ok = 1
            if not ok:
                raise "get_supported_types found badly formed autodock_element", t
        return supported_types


    def set_supported_types(self, type_list):
        self.supported_types = type_list


    def read_parameter_file(self, param_file):
        optr = open(param_file)
        lines = optr.readlines()
        #parse and set values
        Rij = {}
        epsij = {}
        vol = {}
        solpar = {}
        Rij_hb = {}
        epsij_hb = {}
        hbond = {}
        all_types = {}
        for l in lines:
            if l.find("FE_coeff_vdW")==0:
                self.vdw_weight = float(l.split()[1])
            if l.find("FE_coeff_hbond")==0:
                self.hbond_weight = float(l.split()[1])
            if l.find("FE_coeff_estat")==0:
                self.estat_weight = float(l.split()[1])
            if l.find("FE_coeff_desolv")==0:
                self.dsolv_weight = float(l.split()[1])
            if l.find("FE_coeff_tors")==0:
                self.tors_weight = float(l.split()[1])
            if l.find("atom_par")==0:
                ll = l.split()
                atomT = ll[1]
                all_types[atomT] = 1
                r,eps, v, sp, Rhb, ehb = map( float, ll[2:8])
                hb = int(ll[8])
                t = atomT+atomT
                Rij[t] = r
                epsij[t] = eps
                vol[atomT] = v
                solpar[atomT] = sp 
                Rij_hb[t] = Rhb 
                epsij_hb[t] = ehb 
                hbond[atomT] = hb
        #parcel out this new information to the various scorers:               
        #electrostatics:
        #newhb
        #keys are OAHD HDOA NAHD HDNA SAHD HDSA
        #Rij_hb and epsij_hb
        hbondT = self.terms[1][0]
        vdwT = self.terms[2][0]
        don_keys = []
        acc_keys = []
        for k,v in hbond.items():
            if v in [1,2]:
                don_keys.append(k)
            if v >2:
                acc_keys.append(k)
        old_hb_Rij = hbondT.Rij
        old_hb_epsij = hbondT.epsij
        old_vdw_Rij = vdwT.Rij
        old_vdw_epsij = vdwT.epsij
        hbondT.Rij = {}
        hbondT.epsij = {}
        vdwT.Rij = {}
        vdwT.epsij = {}
        #newvdw
        for t, val in Rij.items():
            vdwT.Rij[t] = val
            hbondT.Rij[t] = 0
        for t,val in epsij.items():
            vdwT.epsij[t] = val
            hbondT.epsij[t] = 0
        #then override the hbonders
        for t1 in acc_keys:
            for t2 in don_keys:
                hbondT.Rij[t1+t2] = Rij_hb[t1+t1]  #the value is in the donor entry only
                hbondT.Rij[t2+t1] = Rij_hb[t1+t1]  #the value is in the donor entry only
                hbondT.epsij[t1+t2] = epsij_hb[t1+t1]
                hbondT.epsij[t2+t1] = epsij_hb[t1+t1]
                vdwT.Rij[t1+t2] = 0 
                vdwT.Rij[t2+t1] = 0 
        #newdsolv
        self.terms[3][0].Solpars.update(solpar)
        self.terms[3][0].Vols.update(vol)
        self.supported_types = self.get_supported_types()


    def get_score(self):
        if self.ms is None:
            raise RuntimeError("no molecular system available in scorer")
        #replaced use of get_score_array because don't understand hbond_array
        #special handling
        score = 0.0
        for term, weight in self.terms:
            score = score + weight*term.get_score()
        #array = self.get_score_array()
        torsEnrg = 0
        if self.exclude_torsFreeEnergy==False:
            lig = self.ms.get_entities(self.ms.configuration[1])[0].top
            torsEnrg = lig.TORSDOF*self.tors_weight
        if self.verbose: print "torsEnrg=", torsEnrg
        if self.verbose: print "score=", score
        return score + torsEnrg


    def get_score_array(self):
        """ return a list of score for each terms per atoms"""
        # NEED TO CORRECT hbond
        # result = self.scorer.get_score_array()
        sal = score_array_list = []
        for t, w in self.terms:
            sal.append(t.get_score_array()*w)
        self.hbond_array = sal[1]
        result = Numeric.add(sal[0], sal[2])
        result = Numeric.add(result, sal[3])
        self.array = result
        return self.array


    def labels_atoms_w_nrg(self,score_array):
        """ will label each atoms with a nrg score """

        # label each first atom by sum of its vdw interaction energies 
        firstAts  = self.ms.get_entities(0)
        for i in range(len(firstAts)):
            # firstAts[i].vdw_energy = Numeric.add.reduce(score_array[i])
            hbond_val =  min(self.hbond_array[i])+max(self.hbond_array[i])
            setattr(firstAts[i], self.prop, Numeric.add.reduce(score_array[i])+hbond_val)
        # label each second atom by sum of its vdw interaction energies
        secondAts = self.ms.get_entities(1)
        swap_result = Numeric.swapaxes(score_array, 0,1)
        swap_hbond_array = Numeric.swapaxes(self.hbond_array, 0, 1)
        for i in range(len(swap_result)):
            hbond_val =  min(swap_hbond_array[i])+max(swap_hbond_array[i])
            setattr(secondAts[i], self.prop, Numeric.add.reduce(swap_result[i])+hbond_val)      

# AutoDock41.Scorer

        
class AutoGrid4Scorer(WeightedMultiTerm, AutoDockTermWeights4):
    """
A handy scorer for AutoGrid4 atom maps.

Note that the Electrostatics term does not contribute to the atom
maps but is in a map of its own (the .e.map).
ALSO Desolvation term energies are split 
the ligand_charge independent portion is in the atom map:
lig.solpar*rec.vol*sol_fn[dist]+(rec.solpar+solpar_q*rec.charge)*lig.vol*sol_fn[dist]

where as the ligand_charge dependent portion is in a map of its own (the 'd' map):
solpar_q*lig.charge*rec.vol*sol_fn[dist]
"""
    def __init__(self):
        WeightedMultiTerm.__init__(self)
        AutoDockTermWeights4.__init__(self)
        self.add_term(NewHydrogenBonding(), self.hbond_weight)
        self.add_term(NewVanDerWaals(), self.vdw_weight)
        self.add_term(NewDesolvationAtomMap(), self.dsolv_weight)
# AutoGrid4Scorer



if __name__ == '__main__':
    print "Test are in Tests/test_AutoDockScorer.py @@ WRITE ME!!"
    # test_scorer.run_test()


