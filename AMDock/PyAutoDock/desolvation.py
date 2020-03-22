## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: desolvation.py,v 1.12 2007/07/24 17:30:45 vareille Exp $
#


import numpy.oldnumeric as Numeric, math
from scorer import DistDepPairwiseScorer


    
class DesolvationRefImpl(DistDepPairwiseScorer):
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictA.setdefault('AtVol', False) #only rec needs AtVol
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)

        # set up or get desolvation parameters for ligand
        # access these dictionaries with defaults for missing keys
        self.sol_par = {
            'C': 0.004,
            'A': 0.0006} # units of kcals/ Ang**2

        # In Autogrid3, a constant is added to each map according
        # to the sol_const dictionary below. In Autogrid3 the constant
        # is applied to the map independent of the empirical weight.
        # Here, we apply the constant before the weight and must divide
        # the constant by the weight in order to recover the constant when
        # the weight is applied.
        # PROBLEM: our term now knows about its Autogrid3 weight.
        dsolv_weight = 0.1711 # Autogrid3 weight
        self.sol_const = {
            'O': 0.236/dsolv_weight,
            'H': 0.118/dsolv_weight,
            }


    def get_ddsol(self, distance):
        """return distance dependent solvation parameter

        WHERE DID THIS COME FROM??
        ===========================

        Stouten @@ Document this @@
        """
        sigma = 3.6
        minus_inv_two_sigma_sqd = -1.0 / (2.0*(sigma*sigma))
        exponent = minus_inv_two_sigma_sqd*(distance*distance)
        ddsol = math.e**exponent
        return ddsol


    def _f(self, at_a, at_b, dist):
        """Return desolvation energy in kcal/mole.

        Atom Volumes are in units of kcal/mol*Ang**3
        NB: pdbqs volumes are cal/mol*Ang**3 and must be converted!!
            This is done by MolecularSystem.py for now.
        
        In Autodock3.0.5, this term is valid only for C atoms
        in the ligand and is used to descriminate aromatic carbons
        from aliphatic carbons
        """
        elm_a = at_a.autodock_element
        #NB we hope we have checked for AtVol by this point 
        # in the MolecularSystem._check_interface
        vol_a = at_a.AtVol
        elm_b = at_b.autodock_element
        energy = 0.0
        sp = self.sol_par.get(elm_b, 0.0) # dict with default
        if sp != 0.0:
            energy = - 1.0 * sp * vol_a * self.get_ddsol(dist)
        return energy # kcal/mol

    def post_process(self):

        # ligand (by convention)
        atoms_bx = self.ms.configuration[1]
        atoms_b = self.ms.get_entities(atoms_bx)
        
        # get the number of receptor atoms
        atoms_ax = self.ms.configuration[0]
        atoms_a = self.ms.get_entities(0)
        num_R_atoms = len(atoms_a)
        # Oxygen
        # 1.3793 = 0.236/0.1711 (so these are unweighted values here!)
        smeared_Oxygen_sol_const = 1.3793/ num_R_atoms

        # Hydrogen
        # 0.6897 = 0.110/0.1711 (so these are unweighted values here!)
        smeared_Hydrogen_sol_const = 0.6897/ num_R_atoms

        # these desolvation constants come from the gpf "constant" parameter
        # where they are weighted by the desolvation weight (0.1711)

        # get the score array from the derived class
        # self.score_array = self.get_score_array()
        
        for row in xrange(len(atoms_a)):
            # we need to call get_entities to reset the iterator after firts loop
            for i,ats in enumerate(self.ms.get_entities(atoms_bx)):
                element = ats.element
                if element == 'H':
                    self.array[row][i] += smeared_Hydrogen_sol_const
                elif element =='O':
                    self.array[row][i] += smeared_Oxygen_sol_const

Desolvation = DesolvationRefImpl
# Desolvation




class NewDesolvationRefImpl(DistDepPairwiseScorer):

    #Vol = 4/3*pi*r**3 where r is Rij[XX]/2.
    Vols = {}
    Vols["C"] = Vols["C"]  = Vols["A"] = 33.5103
    Vols["N"] = Vols["NA"] = Vols["Na"] = Vols["n"] = 22.4493
    Vols["O"] = Vols["OA"] = Vols["Oa"] = 17.1573
    Vols["P"] = 38.7924
    Vols["S"] = Vols["SA"] = Vols["Sa"] = 33.5103
    Vols["H"] = Vols["HD"] =  Vols["HS"] = Vols["Hd"] = Vols["Hs"] =0.00
    Vols["F"] = 15.448
    Vols["f"] = Vols["FE"] = Vols["Fe"] = 1.84           #Iron oldvalue==1.1503
    Vols["I"] = 55.0585
    Vols["M"] = Vols["MG"] = Vols["Mg"] = 1.56           # Magnesium oldvalue=1.1503
    Vols["MN"]=  2.14                        # Manganese 
    Vols["Z"] = Vols["ZN"] = Vols["Zn"] = 1.70           # Zinc oldvalue = 1.6974
    Vols["L"] = Vols["CA"] = Vols["Ca"] =  2.77           # Calcium oldvalue = 4.0644
    Vols["c"] = Vols["CL"] = Vols["Cl"] = 35.8235         # Chlorine
    Vols["b"] = Vols["BR"] = Vols["Br"] = 42.5661         # Bromine

    # set up or get desolvation parameters
    # access these dictionaries with defaults for missing keys
    Solpars = {                     #oldvalue *  0.10188
                'C': -0.00143,   #oldvalue = -0.00143
                'A': -0.00052,   #oldvalue = -0.00052
                'N': -0.00162,   #oldvalue = -0.00162
                'NA':-0.00162,   #oldvalue = -0.00162
                'O': -0.00251,   #oldvalue = -0.00251
                'OA':-0.00251,   #oldvalue = -0.00251
                'H':  0.00051,   #oldvalue =  0.00051
                'HD': 0.00051,   #oldvalue =  0.00051
                'S': -0.00214,   #oldvalue = -0.00214
                'SA':-0.00214}   #oldvalue = -0.00214
                                # units of kcals/ Ang**2  


    def __init__(self, ms=None, solpar_q = 0.01097): #oldvalue = 0.01097
        DistDepPairwiseScorer.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA = {}
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)

        #set up constant
        self.solpar_q = solpar_q



    def get_ddsol(self, distance):
        """return distance dependent solvation parameter

        WHERE DID THIS COME FROM??
        ===========================

        Stouten @@ Document this @@
        """
        sigma = 3.6
        minus_inv_two_sigma_sqd = -1.0 / (2.0*(sigma*sigma))
        exponent = minus_inv_two_sigma_sqd*(distance*distance)
        ddsol = math.e**exponent
        return ddsol


    def _f(self, at_a, at_b, dist):
        """Return desolvation energy in kcal/mole.

        Atom Volumes are in units of kcal/mol*Ang**3
        NB: pdbqs volumes are cal/mol*Ang**3 and must be converted!!
            This is done by MolecularSystem.py for now.
        
        In Autodock3.0.5, this term is valid only for C atoms
        in the ligand and is used to discriminate aromatic carbons
        from aliphatic carbons
        """
        elm_a = at_a.autodock_element
        charge_a = at_a.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_a = self.Vols.get(elm_a, 33.5103)
        #vol_a = at_a.AtVol
        #-.0.00110*0.10188, the weight from the recalibration
        sp_a = self.Solpars.get(elm_a, -0.00110) # dict with default
        #sp_a = self.Solpars.get(elm_a, 0.0) # dict with default
        #NB we hope we have checked for AtVol by this point 
        # in the MolecularSystem._check_interface
        elm_b = at_b.autodock_element
        charge_b = at_b.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_b = self.Vols.get(elm_b, 33.5103)
        #vol_b = at_b.AtVol
        #-.0.00110*0.10188, the weight from the recalibration
        sp_b = self.Solpars.get(elm_b, -0.00110) # dict with default

        lig_energy = 0.0
        rec_energy = 0.0
        
        sol_func = self.get_ddsol(dist)
        #if sp != 0.0:
        #    energy = - sp * vol_a * self.get_ddsol(dist)
        rec_at_energy = (sp_a + self.solpar_q*abs(charge_a))*vol_b * sol_func
        lig_at_energy = (sp_b + self.solpar_q*abs(charge_b))*vol_a * sol_func
        return rec_at_energy + lig_at_energy # kcal/mol


NewDesolvation = NewDesolvationRefImpl
#end NewDesolvation



class NewDesolvationLigOnlyRefImpl(NewDesolvation):

    #def __init__(self, ms=None, solpar_q=0.01097):
    #    NewDesolvation.__init__(self, ms=ms, solpar_q=solpar_q)


    def _f(self, at_a, at_b, dist):
        """Return desolvation energy in kcal/mole.

        Atom Volumes are in units of kcal/mol*Ang**3
        NB: pdbqs volumes are cal/mol*Ang**3 and must be converted!!
            This is done by MolecularSystem.py for now.
        
        In Autodock3.0.5, this term is valid only for C atoms
        in the ligand and is used to discriminate aromatic carbons
        from aliphatic carbons
        """
        elm_a = at_a.autodock_element
        charge_a = at_a.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_a = self.Vols.get(elm_a, 33.5103)
        #vol_a = at_a.AtVol
        #-.0.00110*0.10188, the weight from the recalibration
        sp_a = self.Solpars.get(elm_a, -0.00110) # dict with default
        #sp_a = self.Solpars.get(elm_a, 0.0) # dict with default
        #NB we hope we have checked for AtVol by this point 
        # in the MolecularSystem._check_interface
        elm_b = at_b.autodock_element
        charge_b = at_b.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_b = self.Vols.get(elm_b, 33.5103)
        #vol_b = at_b.AtVol
        #-.0.00110*0.10188, the weight from the recalibration
        sp_b = self.Solpars.get(elm_b, -0.00110) # dict with default

        lig_energy = 0.0
        rec_energy = 0.0
        
        sol_func = self.get_ddsol(dist)
        #if sp != 0.0:
        #    energy = - sp * vol_a * self.get_ddsol(dist)
        #rec_at_energy = (sp_a + self.solpar_q*abs(charge_a))*vol_b * sol_func
        lig_at_energy = (sp_b + self.solpar_q*abs(charge_b))*vol_a * sol_func
        #return rec_at_energy + lig_at_energy # kcal/mol
        return lig_at_energy

NewDesolvationLigOnly = NewDesolvationLigOnlyRefImpl
#end NewDesolvationLigOnly


#NewDesolvationAtomMap
class NewDesolvationAtomMapRefImpl(NewDesolvation):

    #def __init__(self, ms=None, solpar_q = 0.01097):
    #    NewDesolvation.__init__(self, ms=ms, solpar_q=solpar_q)


    def _f(self, at_a, at_b, dist):
        """Return desolvation energy in kcal/mole.

        Atom Volumes are in units of kcal/mol*Ang**3
        NB: pdbqs volumes are cal/mol*Ang**3 and must be converted!!
            This is done by MolecularSystem.py for now.
        
        In Autodock3.0.5, this term is valid only for C atoms
        in the ligand and is used to discriminate aromatic carbons
        from aliphatic carbons
        """
        elm_a = at_a.autodock_element
        charge_a = at_a.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_a = self.Vols.get(elm_a, 33.5103)
        sp_a = self.Solpars.get(elm_a, -0.00110) # dict with default
        #NB we hope we have checked for AtVol by this point 
        # in the MolecularSystem._check_interface
        elm_b = at_b.autodock_element
        charge_b = at_b.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_b = self.Vols.get(elm_b, 33.5103)
        sp_b = self.Solpars.get(elm_b, -0.00110) # dict with default

        lig_energy = 0.0
        rec_energy = 0.0
        
        sol_func = self.get_ddsol(dist)
        #
        rec_at_energy = (sp_a + self.solpar_q*abs(charge_a))*vol_b * sol_func
        #NOTE THIS IS TRUNCATED:
        #lig_at_energy = (sp_b + self.solpar_q*abs(charge_b))*vol_a * sol_func
        #this portion goes into the atom map
        lig_at_energy = (sp_b)*vol_a * sol_func
        #
        return rec_at_energy + lig_at_energy # kcal/mol

NewDesolvationAtomMap = NewDesolvationAtomMapRefImpl


#NewDesolvationDesolvMap
class NewDesolvationDesolvMapRefImpl(NewDesolvation):

    #def __init__(self, ms=None, solpar_q = 0.01097):
    #    NewDesolvation.__init__(self, ms=ms, solpar_q=solpar_q)


    def _f(self, at_a, at_b, dist):
        """Return desolvation energy in kcal/mole.

        Atom Volumes are in units of kcal/mol*Ang**3
        NB: pdbqs volumes are cal/mol*Ang**3 and must be converted!!
            This is done by MolecularSystem.py for now.
        
        In Autodock3.0.5, this term is valid only for C atoms
        in the ligand and is used to discriminate aromatic carbons
        from aliphatic carbons
        """
        elm_a = at_a.autodock_element
        charge_a = at_a.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_a = self.Vols.get(elm_a, 33.5103)
        sp_a = self.Solpars.get(elm_a, -0.00110) # dict with default
        #NB we hope we have checked for AtVol by this point 
        # in the MolecularSystem._check_interface
        elm_b = at_b.autodock_element
        charge_b = at_b.charge
        #WHAT SHOULD BE A DEFAULT VOLUME? CARBON?
        vol_b = self.Vols.get(elm_b, 33.5103)
        sp_b = self.Solpars.get(elm_b, -0.00110) # dict with default

        lig_energy = 0.0
        rec_energy = 0.0
        
        sol_func = self.get_ddsol(dist)
        #
        #NOTE how following line is truncated:
        #lig_at_energy = (sp_b + self.solpar_q*abs(charge_b))*vol_a * sol_func
        #this portion goes into the atom map
        #lig_at_energy = (sp_b)*vol_a * sol_func + 
        #rec_at_energy = (sp_a + self.solpar_q*abs(charge_a))*vol_b * sol_func

        # for the .d.map:
        lig_at_energy = self.solpar_q*abs(charge_b)*vol_a * sol_func
        ####this was wrong but passed because atom had charge 1.0
        ###lig_at_energy = self.solpar_q*abs(charge_b)*vol_a * sol_func
        lig_at_energy = self.solpar_q * vol_a * sol_func
        return  lig_at_energy # kcal/mol

NewDesolvationDesolvMap = NewDesolvationDesolvMapRefImpl

#end NewDesolvation

if __name__ == '__main__':
    print "run tests in Tests.test_desolvation"
