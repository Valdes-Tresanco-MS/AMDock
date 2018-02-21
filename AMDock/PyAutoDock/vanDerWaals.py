## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: vanDerWaals.py,v 1.19 2008/06/17 22:36:40 rhuey Exp $
#


import math
import numpy.oldnumeric as Numeric

from PyAutoDock.MolecularSystem import MolecularSystem
from PyAutoDock.scorer import DistDepPairwiseScorer

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

    

class VanDerWaalsRefImpl(DistDepPairwiseScorer, HBondVDWSmoothing):
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)


        # These VDW interaction set to 0.0 because the VDW energy
        # is calculated with the HBOND term.
        self.Rij["OH"] = self.Rij["HO"] = 0.0
        self.Rij["NH"] = self.Rij["HN"] = 0.0
        self.Rij["SH"] = self.Rij["HS"] = 0.0

    # set up class variables epsij, Rij
    # Access is through the get_ and set_ methods!!
    # dicts will probably move a class of their own
    Rij = {}
    Rij["CC"] = 4.0
    Rij["AA"] = Rij["CC"]
    Rij["NN"] = 3.5
    Rij["OO"] = 3.2
    Rij["PP"] = 4.2
    Rij["SS"] = 4.0
    Rij["HH"] = 2.0
    Rij["FF"] = 3.09
    Rij["II"] = 4.72
    Rij["MM"] = 1.3          # Magnesium
    Rij["ZZ"] = 1.48         # Zinc
    Rij["LL"] = 1.98         # Calcium
    Rij["nn"] = Rij["NN"]    # non-HB Nitrogen 
    Rij["ff"] = 1.3          # Iron
    Rij["cc"] = 4.09         # Chlorine
    Rij["bb"] = 4.33         # Bromine
    #metals for summarize
    Rij["ZnZn"] = 1.48         # Zinc
    Rij["CaCa"] = 1.98         # Calcium
    Rij["MgMg"] = 1.3          # Magnesium
    Rij["MnMn"] = 1.3          # Magnesium
    Rij["FeFe"] = 1.3          # Iron
    Rij["ClCl"] = 4.09         # Chlorine
    Rij["BrBr"] = 4.33         # Bromine



    def get_Rij(self, a, b):
        """Return Rij of a, b atom-type pair
        
        Add arithmetic mean of Rij[a+a] and Rij[b+b] if necessary
        """
        R = self.Rij
        radius = R.setdefault(a+b, ((R[a+a] + R[b+b])/2.0))
        R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
        return radius


    def set_Rij(self, a, b, radius):
        R = self.Rij
        R[a+b] = R[b+a] = radius


    epsij = {}
    epsij["CC"] = 0.1500
    epsij["AA"] = epsij["CC"]
    epsij["NN"] = 0.1600
    epsij["OO"] = 0.2000
    epsij["PP"] = 0.2000
    epsij["SS"] = 0.2000
    epsij["HH"] = 0.0200
    epsij["FF"] = 0.0800
    epsij["II"] = 0.5520
    epsij["MM"] = 0.8750         # Magnesium
    epsij["ZZ"] = 0.5500         # Zinc
    epsij["LL"] = 0.5500         # Calcium
    epsij["nn"] = epsij["NN"]    # non-HB Nitrogen
    epsij["ff"] = 0.0100         # Iron
    epsij["cc"] = 0.2760         # Chlorine
    epsij["bb"] = 0.3890         # Bromine
    #metals for summarize
    epsij["MgMg"] = 0.8750         # Magnesium
    epsij["MnMn"] = 0.8750         # Magnesium
    epsij["ZnZn"] = 0.5500         # Zinc
    epsij["CaCa"] = 0.5500         # Calcium
    epsij["FeFe"] = 0.0100         # Iron
    epsij["ClCl"] = 0.2760         # Chlorine
    epsij["BrBr"] = 0.3890         # Bromine


    def get_epsij(self, a, b):
        """Return epsij of a, b atom-type pair

        Add geometric mean of epsij[a+a] and epsij[b+b] if necessary
        """
        e = self.epsij
        well_depth = e.setdefault(a+b, math.sqrt( e[a+a]*e[b+b]))
        e[b+a] = well_depth # enforce symmetry (e[ba] = e[ab])
        return well_depth

        
    def set_epsij(self, a, b, well_depth):
        epsij = self.epsij
        epsij[a+b] = epsij[b+a] = well_depth


    def _f(self, at_a, at_b, dist):
        """ vdw pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 6.
        elm_a = at_a.element
        elm_b = at_b.element
        # given the atom types, find epsij and Rij
        epsij = self.get_epsij(elm_a, elm_b)
        Rij = self.get_Rij(elm_a, elm_b)
        if Rij==0.0:
            return 0.
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = dist**exp_B
        rA = dist**exp_A
        # (MS) FIXME: it happens that rA or rB becomes 0.0 and we get
        # ZeroDivisionError: float division
        try:
            energy = cA/rA - cB/rB
        except ZeroDivisionError:
            return 99999.9
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy

VanDerWaals = VanDerWaalsRefImpl
# VanDerWaals



class HydrogenBondingRefImpl(DistDepPairwiseScorer, HBondVDWSmoothing):
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictA.setdefault('bonds', False) #only receptor needs bonds
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)

        # HydrogenBonding specific parameters
        self.Rij = {}
        self.Rij["OH"] = self.Rij["HO"] = 1.90
        self.Rij["NH"] = self.Rij["HN"] = 1.90
        self.Rij["SH"] = self.Rij["HS"] = 2.50

        self.epsij = {}
        self.epsij["OH"] = self.epsij["HO"] = 5.0
        self.epsij["NH"] = self.epsij["HN"] = 5.0
        self.epsij["SH"] = self.epsij["HS"] = 1.0


    def get_Rij(self, a, b):
        """Return Rij of a, b atom-type pair
        Add arithmetic mean of Rij[a+a] and Rij[b+b] to 0. if necessary
        """
        R = self.Rij
        #unknown values are set to 0.
        radius = R.setdefault(a+b, 0.)
        #radius = R.setdefault(a+b, ((R[a+a] + R[b+b])/2.0))
        R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
        return radius


    def get_epsij(self, a, b):
        """Return epsij of a, b atom-type pair

        Add geometric mean of epsij[a+a] and epsij[b+b] to 0. if necessary
        """
        e = self.epsij
        #unknown values are set to 0.
        well_depth = e.setdefault(a+b, 0.)
        e[b+a] = well_depth # enforce symmetry (e[ba] = e[ab])
        return well_depth
        

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
        DistDepPairwiseScorer.set_molecular_system(self, ms)
        entities = self.ms.get_entities(self.ms.configuration[0])
        # calculate vectors
        self.hbvc = HBondVectorCalculator(entities.coords,
                                          entities.autodock_element)


    def _f(self, at_a, at_b, dist):
        """ hbond pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 10.
        elm_a = at_a.element
        elm_b = at_b.element
        coords_a = at_a.coords
        coords_b = at_b.coords
        # return 0 if you don't H bond
        if elm_a+elm_b not in ["OH", "HO", "NH", "HN", "SH", "HS"]:
            return 0.0
        
        exp_B = 10.0 # use 12-10 for Hbond VDW
        
        # given the atom types, find epsij and Rij
        epsij = self.epsij[elm_a+elm_b]
        Rij = self.Rij[elm_a+elm_b]
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        sm_dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = sm_dist**exp_B
        rA = sm_dist**exp_A
        energy = cA/rA - cB/rB

        # maybe get H bond scale factor
        if ((elm_a in ['N', 'O', 'S'] and elm_b == 'H') or
            (elm_b in ['N', 'O', 'S'] and elm_a == 'H')):

            rsph = energy/100.
            rsph = max(rsph, 0.)
            rsph = min(rsph, 1.)

            # hbf (racc or rdon) 
            # a smarter, atom-aware hbond vector calculator...
            hbf = self.hbvc.get_atom_factor(at_a, at_b, sm_dist)
            energy = energy * (hbf + rsph -rsph*hbf)
            
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy 

HydrogenBonding = HydrogenBondingRefImpl
# HydrogenBonding



class HBondVectorCalculator:
    def __init__(self, coords, elements):
        self.coords = coords
        self.elm = elements
        self.rvectors = {}
        
    # vector algebra helper functions
    def cross_product(self, a, b):
        return [ a[1]*b[2] - a[2]*b[1],
                 a[2]*b[0] - a[0]*b[2],
                 a[0]*b[1] - a[1]*b[0]]
    def dot_product(self, a, b):
        return (a[0]*b[0] + a[1]*b[1] + a[2]*b[2])
    def vector(self, a, b):
        return [ b[0]-a[0], b[1]-a[1], b[2]-a[2] ]
    def magnitude(self, a):
        return math.sqrt( a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
    def magnitude_sqrd(self, a):
        return ( a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
    def normalize(self, a, magnitude=None):
        if magnitude is None:
            magnitude = self.magnitude(a)
        return [ a[0]/magnitude, a[1]/magnitude, a[2]/magnitude]
    def scale(self, a, scale):
        return [ a[0]*scale, a[1]*scale, a[2]*scale]
    def vector_sum(self, a, b):
        return [ b[0]+a[0], b[1]+a[1], b[2]+a[2] ]


    def hydrogen_get_rvector(self, hydrogen_ia):
        # hydrogen_ia is an atom
        # cache previously found answers in dict keyed by hydrogen_ia
        key = hydrogen_ia
        if self.rvectors.has_key(key):
            return self.rvectors[key] # reuse answer if possible
        
        # find the neighbor atom bonded to this Hydrogen
        assert (len(hydrogen_ia.bonds)), \
               "Non-bonded %s: %s, index %d" % \
               (hydrogen_ia.element, hydrogen_ia.name,
                self.coords.index(hydrogen_ia.coords))
                
        bond = hydrogen_ia.bonds[0]
        bonded_atom = bond.atom1
        if bonded_atom == hydrogen_ia:
            bonded_atom = bond.atom2

        bonded_elm = bonded_atom.element
        if bonded_elm in ['N', 'O']:
            # find the difference vector from Hydrogen to the N or O
            diff = self.vector(bonded_atom.coords, hydrogen_ia.coords)
            dist_sqrd = self.magnitude_sqrd(diff)
            assert( dist_sqrd < 1.69 ) # or else that bond was too long!
            magnitude = math.sqrt(dist_sqrd)
            rvect = self.normalize(diff, magnitude)
            self.rvectors[key] = (rvect, bonded_elm) # save answer
            return rvect, bonded_elm
        else:
            # we found a Hydrogen bonded to something other than N or O
            # and this Hydrogen should not form Hydrogen bonds !!
            self.rvectors[key] = ((0., 0., 0.), bonded_elm)
            return (0.,0.,0.), bonded_elm


    def oxygen_get_rvector(self, oxygen_ia):
        coords = oxygen_ia.coords
        # cache previously found answers in dict keyed by oxygen_ia
        key = tuple(coords)
        if self.rvectors.has_key(key):
            return self.rvectors[key] # reuse answer is possible

        # not found in self.rvectors so, calculate for the first time

        # find the neighbor atom bonded to this Oxygen
        nbond = len(oxygen_ia.bonds)
        assert (nbond), "Non-bonded %s: %s, index %d" % \
               (oxygen_ia.element, oxygen_ia.name,
                self.coords.index(oxygen_ia.coords))
        
        # now, branch on nbond == 0, 1, or 2
        
        if nbond == 1: # one bond: carbonyl oxygen O=C-X
            # get carbonyl carbon
            bond = oxygen_ia.bonds[0]
            carbonyl_carbon = bond.atom1
            if carbonyl_carbon == oxygen_ia:
                carbonyl_carbon = bond.atom2
            # now we know carbonyl_carbon
            coords_i1 = carbonyl_carbon.coords
                
            # calculate normalized carbonyl bond vector rvector[ia][]
            rvect_i1 = self.normalize(self.vector(coords_i1, coords))

            # find second atom (i2) bonded to carbonyl carbon (i1)
            bond = carbonyl_carbon.bonds[-1] # see NOTE (30 lines down)
            if bond.atom1 == oxygen_ia or bond.atom2 == oxygen_ia:
                # skip it - this is the carbonyl bond itself
                bond = carbonyl_carbon.bonds[-2] # see NOTE (30 lines down)
            bonded_atom_i2 = bond.atom1
            if bonded_atom_i2 == carbonyl_carbon:
                bonded_atom_i2 = bond.atom2
            # now we know bonded_atom_i2
            coords_i2 = bonded_atom_i2.coords
            elm_i2 = bonded_atom_i2.element
            
            # now bonded_atom_i2 is an atom bound to the carbonyl carbon
            # but NOT the carbonyl oxygen

            diff = self.vector(bonded_atom_i2.coords, carbonyl_carbon.coords)
            dist_sqrd = self.magnitude_sqrd(diff)
            assert ((dist_sqrd < 1.69 and elm_i2 == 'H') or
                    (dist_sqrd < 2.89 and elm_i2 != 'H')), "Bad bond length"
            
            # rvect_i2 is vector from carbonyl carbon to second atom
            rvect_i2 = self.normalize(
                self.vector(coords_i1, coords_i2))
                
            # C=O (rvect_i1) CROSS C-X (rvect_i2) gives lone pair
            # plane normal
            unit_lp_normal = self.normalize(
                self.cross_product(rvect_i1, rvect_i2))

            # at this point we could return with the first other
            # atom found, but the C implementation keeps going
            # and returns the LAST other atom found!!
            # NOTE:
            # That comment refers to a linear search through the atoms
            # that went away when we used the bond information.
            # The reason we search backwards through bonds above is
            # to be consistent with the Autodock305 C implementation
            
            # record answer for next time
            self.rvectors[key] = (rvect_i1, unit_lp_normal)
            return (rvect_i1, unit_lp_normal)

        if nbond == 2:
            # find the vector pointing between Oxygen lone pairs
            #    the front will be the Oxygen itself (coords)
            #    the back will be on the vector from i1 to i2 (rvector2)
            #    where the back is on rvector2 is determined by the
            #    projection of rvect_i1 (the vector from i1 to O) onto rvector2
            #
            #                 O (coords)
            #                / \
            #               / ^ \
            #              /  |  \ rvect_i1
            #             /   |   \
            #           i2    |    i1
            #            <-revector2

            bond = oxygen_ia.bonds[0]
            bonded_atom_i1 = bond.atom1
            if bonded_atom_i1 == oxygen_ia:
                bonded_atom_i1 = bond.atom2
            # now we know bonded_atom_i1
            coords_i1 = bonded_atom_i1.coords

            bond = oxygen_ia.bonds[1]
            bonded_atom_i2 = bond.atom1
            if bonded_atom_i2 == oxygen_ia:
                bonded_atom_i2 = bond.atom2
            # now we know bonded_atom_i2
            coords_i2 = bonded_atom_i2.coords

            # normalized vector from coords_i1 to coords_i2
            rvector2 = self.normalize(self.vector(coords_i1, coords_i2))

            # find point along rvectcor2 to 
            rdot = self.dot_product( self.vector(coords_i1, coords), rvector2)
            rvector = self.normalize(
                self.vector( self.vector_sum( self.scale(rvector2, rdot),
                                              coords_i1),
                             coords))

            # record answer for next time
            self.rvectors[key] = (rvector, rvector2)
            return self.rvectors[key] # return tuple

        if nbond >= 3:
            raise "Three(or more)-bonded %s: %s, index %d" % \
                  (oxygen_ia.element, oxygen_ia.name,
                   self.coords.index(oxygen_ia.coords))
        

    def get_atom_factor(self, atom_ia, probe, dist):
        elm_ia = atom_ia.autodock_element
        coords_ia = atom_ia.coords
        elm_probe = probe.autodock_element
        coords_probe = probe.coords
            
        # get difference vector to the probe and normalize it
        d = self.normalize(self.vector(coords_probe, coords_ia))
        
        # get vector to the potential hbond position
        if elm_ia == 'H':
            (rvector, bonded_element) = self.hydrogen_get_rvector(atom_ia)
            # how does probe atom compare to rvector?
            # cos_theta = d dot rvector (cosine of angle subtended)
            #
            # I don't get this. Usually, "a dot b = |a||b|cos(theta)"
            # 
            cos_theta = -self.dot_product(d, rvector)

            if (cos_theta <= 0.0):
                return 0.0 # no hbond possible at this angle

            # find what type of atom is bonded
            exp = 1.0
            if bonded_element == 'N':
                exp = 2.
            elif bonded_element == 'O':
                exp = 4.
            return pow(cos_theta, exp)

        elif elm_ia == 'O':
            (rvector, rvector2) = self.oxygen_get_rvector(atom_ia)
            # how does probe atom compare to rvector?
            # cos_theta = d dot rvector (cosine of angle subtended)
            cos_theta = -self.dot_product(d, rvector)
            
            # see Goodford (1989) Table II.
            
            # t0 is the angle out of the lone pair plane calculated
            # as 90 degrees - acos(vector to grid point ('d') DOT lone pair
            # plane normal ('rvector2'))
            t0 = -self.dot_product(d, rvector2)

            # I think this enforces the angular range of Et ??
            if (t0 > 1.0):  t0 = 1.0
            if (t0 < -1.0): t0 = -1.0
            t0 = (math.pi/2.0) - math.acos(t0)

            # ti is the angle in the lone pair plane away from the vector
            # between the lone pairs ('rvector'),
            # calculated as the(grid vector ('d' CROSS lone pair plane normal
            # ('rvector2')) DOT C=O vector ('rvector') - 90 degrees)
            ti = self.dot_product(rvector, self.normalize(
                self.cross_product(d, rvector2)))

            rdon = 0.0
            if (cos_theta >= 0.0):
                # make sure ti is between -1.0 and 1.0
                if (ti > 1.0):    ti = 1.0
                elif (ti < -1.0): ti = -1.0
                ti = abs(math.acos(ti) - (math.pi/2.0))
                rdon = (0.9 + 0.1*math.sin(2.0*ti))*math.cos(t0)
            elif (cos_theta >= -0.34202):
                rdon =  562.25*pow((0.116978- cos_theta*cos_theta),
                                   3.)*math.cos(cos_theta)
            return rdon
        else:
            return 1.0 # was that a sulphur?
# HBondVectorCalculator



class NewHBondVectorCalculator(HBondVectorCalculator):

    def hydrogen_get_rvector(self, hydrogen_ia):
        # if we know about this atom then return what we know
        #this differs from HBVC only in elm[0]
        key = hydrogen_ia
        if self.rvectors.has_key(key):
            return self.rvectors[key] #reuse answer if possible

       # find the neighbor atom bonded to this Hydrogen
        assert (len(hydrogen_ia.bonds)), \
               "Non-bonded %s: %s, index %d" % \
               (hydrogen_ia.element, hydrogen_ia.name,
                self.coords.index(hydrogen_ia.coords))
                
        bond = hydrogen_ia.bonds[0]
        bonded_atom = bond.atom1
        if bonded_atom == hydrogen_ia:
            bonded_atom = bond.atom2

        bonded_elm = bonded_atom.element
        if bonded_elm[0] in ['N', 'O']:
                    # find the difference vector from Hydrogen to the N or O
                    # or S ???
            diff = self.vector(bonded_atom.coords, hydrogen_ia.coords)
            dist_sqrd = self.magnitude_sqrd(diff)
            #what about H-S???
            assert( dist_sqrd < 1.69 ) # or else that bond was too long!
            magnitude = math.sqrt(dist_sqrd)
            rvect = self.normalize(diff, magnitude)
            self.rvectors[key] = (rvect, bonded_elm) # save answer
            return rvect, bonded_elm
        else:
            # we found a Hydrogen bonded to something other than N or O
            # and this Hydrogen should not form Hydrogen bonds !!
            self.rvectors[key] = ((0., 0., 0.), bonded_elm)
            #IS THIS THE RIGHT THING TO DO?
            return (0.,0.,0.), bonded_elm


    def oxygen_get_rvector(self, oxygen_ia):
        coords = oxygen_ia.coords
        # cache previously found answers in dict keyed by oxygen_ia
        key = tuple(coords)
        if self.rvectors.has_key(key):
            return self.rvectors[key] # reuse answer is possible

        # not found in self.rvectors so, calculate for the first time

        # find the neighbor atom bonded to this Oxygen
        nbond = len(oxygen_ia.bonds)
        assert (nbond), "Non-bonded %s: %s, index %d" % \
               (oxygen_ia.element, oxygen_ia.name,
                self.coords.index(oxygen_ia.coords))
        
        # now, branch on nbond == 0, 1, or 2
        
        if nbond == 1: # one bond: O=C-X
                       # could be O=S-X
            # get neighbor atom 
            bond = oxygen_ia.bonds[0]
            neighbor_atom = bond.atom1
            if neighbor_atom == oxygen_ia:
                neighbor_atom = bond.atom2
            # now we know neighbor_atom
            coords_i1 = neighbor_atom.coords
                
            # calculate normalized neighbor_atom bond vector rvector[ia][]
            rvect_i1 = self.normalize(self.vector(coords_i1, coords))

            # find second atom (i2) bonded to neighbor_atom (i1)
            bond = neighbor_atom.bonds[-1] # see NOTE (30 lines down)
            if bond.atom1 == oxygen_ia or bond.atom2 == oxygen_ia:
                # skip it - this is the neighbor_atom bond itself
                bond = neighbor_atom.bonds[-2] # see NOTE (30 lines down)
            bonded_atom_i2 = bond.atom1
            if bonded_atom_i2 == neighbor_atom:
                bonded_atom_i2 = bond.atom2
            # now we know bonded_atom_i2
            coords_i2 = bonded_atom_i2.coords
            elm_i2 = bonded_atom_i2.element
            
            # now bonded_atom_i2 is an atom bound to the neighbor_atom 
            # but NOT the neighbor_atom oxygen

            diff = self.vector(bonded_atom_i2.coords, neighbor_atom.coords)
            dist_sqrd = self.magnitude_sqrd(diff)
            
            assert ((dist_sqrd < 1.69 and elm_i2 == 'H') or
                    (neighbor_atom.element=='S' and dist_sqrd <3.5 and elm_i2 == 'C') or
                    (dist_sqrd < 2.89 and elm_i2 != 'H')), "Bad bond length"
            
            # rvect_i2 is vector from neighbor_atom carbon to second atom
            rvect_i2 = self.normalize(
                self.vector(coords_i1, coords_i2))
                
            # C=O (rvect_i1) CROSS C-X (rvect_i2) gives lone pair
            # plane normal
            unit_lp_normal = self.normalize(
                self.cross_product(rvect_i1, rvect_i2))

            # at this point we could return with the first other
            # atom found, but the C implementation keeps going
            # and returns the LAST other atom found!!
            # NOTE:
            # That comment refers to a linear search through the atoms
            # that went away when we used the bond information.
            # The reason we search backwards through bonds above is
            # to be consistent with the Autodock305 C implementation
            
            # record answer for next time
            self.rvectors[key] = (rvect_i1, unit_lp_normal)
            return (rvect_i1, unit_lp_normal)

        if nbond == 2:
            # find the vector pointing between Oxygen lone pairs
            #    the front will be the Oxygen itself (coords)
            #    the back will be on the vector from i1 to i2 (rvector2)
            #    where the back is on rvector2 is determined by the
            #    projection of rvect_i1 (the vector from i1 to O) onto rvector2
            #
            #                 O (coords)
            #                / \
            #               / ^ \
            #              /  |  \ rvect_i1
            #             /   |   \
            #           i2    |    i1
            #            <-revector2

            bond = oxygen_ia.bonds[0]
            bonded_atom_i1 = bond.atom1
            if bonded_atom_i1 == oxygen_ia:
                bonded_atom_i1 = bond.atom2
            # now we know bonded_atom_i1
            coords_i1 = bonded_atom_i1.coords

            bond = oxygen_ia.bonds[1]
            bonded_atom_i2 = bond.atom1
            if bonded_atom_i2 == oxygen_ia:
                bonded_atom_i2 = bond.atom2
            # now we know bonded_atom_i2
            coords_i2 = bonded_atom_i2.coords

            # normalized vector from coords_i1 to coords_i2
            rvector2 = self.normalize(self.vector(coords_i1, coords_i2))

            # find point along rvectcor2 to 
            rdot = self.dot_product( self.vector(coords_i1, coords), rvector2)
            rvector = self.normalize(
                self.vector( self.vector_sum( self.scale(rvector2, rdot),
                                              coords_i1),
                             coords))

            # record answer for next time
            self.rvectors[key] = (rvector, rvector2)
            return self.rvectors[key] # return tuple

        if nbond >= 3:
            raise "Three(or more)-bonded %s: %s, index %d" % \
                  (oxygen_ia.element, oxygen_ia.name,
                  self.coords.index(oxygen_ia.coords))



    #def nitrogen_get_rvector(self, coords):
    def nitrogen_get_rvector(self, nitrogen_ia):
        coords = nitrogen_ia.coords
        key = tuple(coords)
        if self.rvectors.has_key(key):
            return self.rvectors[key] # reuse answer
        # not found in self.rvectors so, calculate for the first time

    
        nbond = len(nitrogen_ia.bonds)
        assert (nbond), "Non-bonded %s: %s, index %d" % \
               (nitrogen_ia.element, nitrogen_ia.name,
                self.coords.index(nitrogen_ia.coords))

        bond = nitrogen_ia.bonds[0]
        il = bond.atom1
        if il==nitrogen_ia:
            il = bond.atom2
        coords_i1 = il.coords
        # now we know nbond, i1, 
        if nbond == 1: # one bond: azide -  :N=C-X
            # calculate normalized carbonyl bond vector rvector[ia][]
            self.rvectors[key] = self.normalize(self.vector(coords_i1, coords))
            return self.rvectors[key]

        #coords_i2 = self.coords[i2]
        #here we also have i2 
        i2 = nitrogen_ia.bonds[1].atom1
        if i2==nitrogen_ia:
            i2 = nitrogen_ia.bonds[1].atom2
        coords_i2 = i2.coords

        if nbond == 2: # two bonds: X1-N=X2
            # get vector from coords to midpoint of i1 and i2
            self.rvectors[key] = self.normalize(self.vector(
                self.scale(self.vector_sum(coords_i1, coords_i2), 0.5),
                coords))
            return self.rvectors[key]

        #coords_i3 = self.coords[i3]
        # get vector from coords to midpoint of i1, i2, and i3
        # here we have i3 also!!!
        i3 = nitrogen_ia.bonds[2].atom1
        if i3==nitrogen_ia:
            i3 = nitrogen_ia.bonds[2].atom2
        coords_i3 = i3.coords
        if nbond == 3: # three bonds: X1, X2, X3
            self.rvectors[key] = self.normalize(self.vector(
                self.scale(self.vector_sum(self.vector_sum(coords_i1,
                                                           coords_i2),
                                           coords_i3),
                           (1./3.)),
                coords))
            return self.rvectors[key]


    #def get_atom_factor(self, dist, elm_ia, coords_ia, elm_probe, coords_probe):
    def get_atom_factor(self, atom_ia, probe, dist):
        elm_ia = atom_ia.autodock_element
        coords_ia = atom_ia.coords
        elm_probe = probe.autodock_element
        coords_probe = probe.coords

        # get difference vector to the probe and normalize it
        d = self.normalize(self.vector(coords_probe, coords_ia))
        
        # get vector to the potential hbond position
        #@@!! FIX THIS !!
        if elm_ia[0] == 'H':
        #if elm_ia == 'HD':
            (rvector, bonded_element) = self.hydrogen_get_rvector(atom_ia)
            # how does probe atom compare to rvector?
            # cos_theta = d dot rvector (cosine of angle subtended)
            #
            # I don't get this. Usually, "a dot b = |a||b|cos(theta)"
            # 
            cos_theta = -self.dot_product(d, rvector)

            if (cos_theta <= 0.0):
                return 0.0 # no hbond possible at this angle

            # find what type of atom is bonded
            exp = 1.0
            #if bonded_element == 'N':
            if bonded_element[0] == 'N':
                exp = 2.
            elif bonded_element[0] == 'O' or bonded_element[0] == 'S':
                #elif bonded_element == 'O':
                exp = 4.
            return pow(cos_theta, exp)

            # @@ NEW @@ need to find closest H and modify accordingly
            #
            #

        elif elm_ia[0] == 'O':
            #elif elm_ia == 'OA':
            #@@!! FIX THIS !!
            (rvector, rvector2) = self.oxygen_get_rvector(atom_ia)
            # how does probe atom compare to rvector?
            # cos_theta = d dot rvector (cosine of angle subtended)
            cos_theta = -self.dot_product(d, rvector)
            
            # see Goodford (1989) Table II.
            
            # t0 is the angle out of the lone pair plane calculated
            # as 90 degrees - acos(vector to grid point ('d') DOT lone pair
            # plane normal ('rvector2'))
            t0 = -self.dot_product(d, rvector2)

            # I think this enforces the angular range of Et ??
            if (t0 > 1.0):  t0 = 1.0
            if (t0 < -1.0): t0 = -1.0
            t0 = (math.pi/2.0) - math.acos(t0)

            # ti is the angle in the lone pair plane away from the vector
            # between the lone pairs ('rvector'),
            # calculated as the(grid vector ('d' CROSS lone pair plane normal
            # ('rvector2')) DOT C=O vector ('rvector') - 90 degrees)
            ti = self.dot_product(rvector, self.normalize(
                self.cross_product(d, rvector2)))

            rdon = 0.0
            
            if (cos_theta >= 0.0):
                # make sure ti is between -1.0 and 1.0
                if (ti > 1.0):    ti = 1.0
                elif (ti < -1.0): ti = -1.0
                    
                ti = abs(math.acos(ti) - (math.pi/2.0))
                
                rdon = (0.9 + 0.1*math.sin(2.0*ti))*math.cos(t0)

            elif (cos_theta >= -0.34202):
                rdon =  562.25*pow((0.116978- cos_theta*cos_theta),
                                   3.)*math.cos(cos_theta)
            return rdon
        elif elm_ia[0] == 'N':
            rvector = self.nitrogen_get_rvector(atom_ia)
            cos_theta = -self.dot_product(d, rvector)
            if (cos_theta <= 0.0):
                return 0.0 # no hbond possible at this angle
            return cos_theta*cos_theta
        else:
            return 1.0 # was that a sulphur?
# NewHBondVectorCalculator


class HydrogenBonding12_10(HydrogenBonding):
    def __init__(self, ms=None):
        HydrogenBonding.__init__(self)
        self.required_attr_dictA.setdefault('bonds', True) #no rec bonds nec.


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
        DistDepPairwiseScorer.set_molecular_system(self, ms)
        entities = self.ms.get_entities(self.ms.configuration[0])
        # calculate vectors


    def _f(self, at_a, at_b, dist):
        """ vdw pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 10.
        elm_a = at_a.element
        elm_b = at_b.element
        # HARDWIRE allowed hydrogen bonding pairs
        if elm_a+elm_b not in ["OH", "HO", "NH", "HN", "SH", "HS"]:
            return 0.0
        # given the atom types, find epsij and Rij
        epsij = self.get_epsij(elm_a, elm_b)
        Rij = self.get_Rij(elm_a, elm_b)
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = dist**exp_B
        rA = dist**exp_A
        # (MS) FIXME: it happens that rA or rB becomes 0.0 and we get
        # ZeroDivisionError: float division
        try:
            energy = cA/rA - cB/rB
        except ZeroDivisionError:
            return 99999.9
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy

# HydrogenBonding12_10



#NEW HB
class NewHydrogenBondingRefImpl(DistDepPairwiseScorer, HBondVDWSmoothing):
    """This extends the HydrogenBonding class by (1) adding new
    rfactors for Nitrogen (before none were used), (2) clamping _hbond values 
    for NH and H-x _hbond values to the energy of a single hbond, 
    (3)implementing a new _hbond value for -O->H- interactions composed of 
    two parts: 1.the interaction of the oxygen with the closest hydrogen 
    plus 2. interactions between the oxygen and the other hydrogen atoms 
    which are are modified by a cosine ramp function 
        Hramp=0.5+0.5cos(theta * 120deg/90deg) 
    where theta is the angle between the vectors from the oxygen
    atom in the probe to the two hydrogen atoms in the receptor so the 
    energy contribution for each other hydrogen is
        Hramp * energy * (hbf + rsph - rsph*hbf) where
    hbf is hbvc.get_atom_factor(at_a, at_b, sm_dist)
    rsph = energy/100. ( 0<=rsph<=1.)
    """
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictA.setdefault('bonds', False) #only receptor needs bonds
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)

        # HydrogenBonding specific parameters
        self.Rij = {}
        self.Rij["OAHD"] = self.Rij["HDOA"] = 1.90
        self.Rij["NAHD"] = self.Rij["HDNA"] = 1.90
        self.Rij["SAHD"] = self.Rij["HDSA"] = 2.50

        self.epsij = {}
        self.epsij["OAHD"] = self.epsij["HDOA"] = 5.0
        self.epsij["NAHD"] = self.epsij["HDNA"] = 5.0
        self.epsij["SAHD"] = self.epsij["HDSA"] = 1.0


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
        DistDepPairwiseScorer.set_molecular_system(self, ms)
        # get ms information
        self.entity_ix = self.ms.configuration[0]
        self.entity_jx = self.ms.configuration[1]
        self.entities_a = self.ms.get_entities(self.entity_ix)
        self.entities_b = self.ms.get_entities(self.entity_jx)
        #NOTE: lenB must be passed in as a parameter for AutoGrid
        if hasattr(ms, 'lenB'):
            self.lenB = ms.lenB
        else:
            self.lenB = len(self.entities_b)
        # calculate vectors
        self.hbvc = NewHBondVectorCalculator(self.entities_a.coords,
                                             self.entities_a.autodock_element)


    def calc_closestH(self, dist_matrix):
        #foreach ligand oxygen atom, find the closest hydrogen in the receptor
        #for each coords in subsetB, find index of closest H in subsetA
        lenA = len(self.entities_a)
        #lenB = len(self.entities_b)
        #set index of closest to 0 to start
        self.closestH = Numeric.zeros(self.lenB,'i')
        #5/16:self.closestH = Numeric.zeros(lenA,'i')
        
        #make list with 'True' for positions of hydrogen in subsetA
        map_A_Hs = map(lambda x: x=='HD', self.entities_a.autodock_element)
        mask_A_Hs = Numeric.logical_and(Numeric.array(map_A_Hs),1)
        for i in xrange(self.lenB):
            #zero out distances to any non-hydrogen atoms in A
            list_i_Hs = (mask_A_Hs*Numeric.array(dist_matrix)[:,i]).tolist()
            #distance to closest hydrogen is the min of the list of distances
            # to hydrogens
            min_i = 9999999.
            for j in xrange(lenA):
                newVal = list_i_Hs[j]
                if newVal!=0. and newVal<min_i:
                    min_i = newVal
            #the index of this closest hydrogen is the index of this distance
            # in the list of distances to hydrogens
            if min_i!=9999999:
                index_min_i = list_i_Hs.index(min_i)
                #save this as the closest hydrogen to this atom in ligand
                self.closestH[i] = index_min_i
            else:
                #there could be NO close hydrogen
                self.closestH[i] = -1
            
        
    #def _hbond(self, dist, elm_a, coords_a,
    #           elm_b, coords_b, exp_A=12.0, exp_B=6.0):

    def _f(self, at_a, at_b, dist, bx):
        """ new hbond pairwise dist dep function
        """
        
        exp_A = 12.
        exp_B = 10.0 # use 12-10 for Hbond VDW
        elm_a = at_a.autodock_element
        elm_b = at_b.autodock_element
        coords_a = at_a.coords
        coords_b = at_b.coords

        # return 0 if you don't H bond
        if elm_a+elm_b not in ["OAHD", "HDOA", "NAHD", "HDNA", "SAHD", "HDSA"]:
            return 0.0
        
        # given the atom types, find epsij and Rij
        epsij = self.epsij[elm_a + elm_b]
        Rij = self.Rij[elm_a + elm_b]
        
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        sm_dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = sm_dist**exp_B
        rA = sm_dist**exp_A
        energy = cA/rA - cB/rB

        # maybe get H bond scale factor
        Hramp = 1.0
            
        if ((elm_a in ['NA', 'OA', 'SA'] and elm_b == 'HD') or
            (elm_b in ['NA', 'OA', 'SA'] and elm_a == 'HD')):

            rsph = energy/100.
            rsph = max(rsph, 0.)
            rsph = min(rsph, 1.)

            # hbf (racc or rdon)
            hbf = self.hbvc.get_atom_factor(at_a, at_b, sm_dist)
            if elm_b=='OA':
                #only recalculate if indexA!=closestH[indexB]
                #indexA = self.entities_a.index(at_a) # @@ are index calls expensive ??!!
                #indexB = self.entities_b.index(at_b) # @@ are index calls expensive ??!!
                #closestH_ix = self.closestH[indexB]
                closestH_ix = self.closestH[bx]
                if closestH_ix == -1:
                    #there are no hydrogens to hbond to this oxygen
                    return 0.

                closestH_atom = self.entities_a[closestH_ix]
                if closestH_atom != at_a:
                    #rv_closestH = self.hbvc.hydrogen_get_rvector(closestH_coords)[0]
                    #rv_currentH = self.hbvc.hydrogen_get_rvector(coords_a)[0]
                    rv_closestH = self.hbvc.hydrogen_get_rvector(closestH_atom)[0]
                    rv_currentH = self.hbvc.hydrogen_get_rvector(at_a)[0]
                    cos_theta = self.hbvc.dot_product(rv_closestH, rv_currentH)
                    theta = math.acos(round(cos_theta, 6))
                    Hramp = 0.5 - 0.5*math.cos(theta *120./90.)
            energy = Hramp * energy * (hbf + rsph -rsph*hbf)
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy 


    #FIX THIS:!!!
    def get_score_array(self):
        """return New Hydrogen bonding array (new term 12/2003).
        """
        entity_ix = self.ms.configuration[0]
        entity_jx = self.ms.configuration[1]
        distance = self.ms.get_dist_mat(entity_ix, entity_jx)
        #distance = self.ms.get_dist_mat(self.entity_ix, self.entity_jx)
        #setup self.closestH array here
        #self.calc_closestH(dist_matrix)
        self.calc_closestH(distance)

        # construct 2D array
        array = []
        #a_atoms = self.entities_a
        #b_atoms = self.entities_b
        cut = self.non_bonded_cutoff
        if self.use_non_bond_cutoff==True:
            for ax, at_a in  enumerate(self.ms.get_entities(entity_ix)):
                array.append([]) # a new row for every atom in first set
                row = array[ax]
                for bx, at_b in  enumerate(self.ms.get_entities(entity_jx)):
                    d = distance[ax][bx]
                    atom_score = 0.0
                    # Obey non-bonded distance cutoff
                    if (d < cut):
                        atom_score = self._f(at_a, at_b, d, bx)
                    row.append(atom_score)
        else: # no cut_off
            for ax, at_a in  enumerate(self.ms.get_entities(entity_ix)):
                array.append([]) # a new row for every atom in subsetA
                row = array[ax]  # the 
                for bx, at_b in  enumerate(self.ms.get_entities(entity_jx)):
                    atom_score = self._f(at_a, at_b, distance[ax][bx], bx )
                    row.append(atom_score)

        #return Numeric.array(array)
        array =  Numeric.array(array)
        # ADJUST array before returning:
        #
        # For N (NA) and H (HD) which accept hbonds, and are part of
        # map or ligand (subsetB) find min and max entries in array,
        # set all others to 0.0. This is to enforce the idea that N
        # and H can only form a single Hbond.

        # if elm_b is N or H make all terms in col 0
        # except max and min for that column
        #for i in xrange(len(self.subsetB_elm)):
        #for ix, b_atom in xrange(len(self.ms.lenB)):
        for bx, at_b in  enumerate(self.ms.get_entities(entity_jx)):
            #if b_atoms[i].autodock_element in ['NA','HD']:
            if at_b.autodock_element in ['NA','HD']:
                # create column to query and throw away
                col = array[:, bx-1].tolist()
                max_val = max(col)
                max_ix = col.index(max_val)
                min_val = min(col)
                min_ix = col.index(min_val)
                # zero out column in self.array
                #for j in xrange(len(self.subsetA_elm)):
                #for j in xrange(len(a_atoms)):
                for ax, at_a in  enumerate(self.ms.get_entities(entity_ix)):
                    #self.array[j,i] = 0.
                    array[ax-1,bx-1] = 0.
                # replace max and mix values
                array[max_ix,bx-1] = max_val
                array[min_ix,bx-1] = min_val

        return array


NewHydrogenBonding = NewHydrogenBondingRefImpl
# NewHydrogenBonding



class NewVanDerWaalsRefImpl(DistDepPairwiseScorer, HBondVDWSmoothing):
    def __init__(self, ms=None):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)

        #new ad_types
        self.Rij["OAHD"] = self.Rij["HDOA"] = 0.0
        self.Rij["NAHD"] = self.Rij["HDNA"] = 0.0
        self.Rij["SAHD"] = self.Rij["HDSA"] = 0.0


    # set up class variables epsij, Rij
    # Access is through the get_ and set_ methods!!
    # dicts will probably move a class of their own

    Rij = {}
    Rij["CC"] = 4.0
    Rij["AA"] = Rij["CC"]
    Rij["NN"] = 3.5
    Rij["OO"] = 3.2
    Rij["PP"] = 4.2
    Rij["SS"] = 4.0
    Rij["HH"] = 2.0
    Rij["FF"] = 3.09
    Rij["II"] = 4.72
    Rij["NANA"] = 3.5
    Rij["OAOA"] = 3.2
    Rij["SASA"] = 4.0
    Rij["HDHD"] = 2.0
    Rij["MGMG"] = 1.3          # Magnesium
    Rij["MNMN"] = 1.3          # Manganese
    Rij["ZNZN"] = 1.48         # Zinc
    Rij["CACA"] = 1.98         # Calcium
    Rij["FEFE"] = 1.3          # Iron
    Rij["CLCL"] = 4.09         # Chlorine
    Rij["BRBR"] = 4.33         # Bromine
    #
    Rij["MgMg"] = 1.3          # Magnesium
    Rij["MnMn"] = 1.3          # Manganese
    Rij["ZnZn"] = 1.48         # Zinc
    Rij["CaCa"] = 1.98         # Calcium
    Rij["FeFe"] = 1.3          # Iron
    Rij["ClCl"] = 4.09         # Chlorine
    Rij["BrBr"] = 4.33         # Bromine


    def get_Rij(self, a, b):
        """Return Rij of a, b atom-type pair
        
        Add arithmetic mean of Rij[a+a] and Rij[b+b] if necessary
        """
        R = self.Rij
        radius = R.setdefault(a+b, ((R[a+a] + R[b+b])/2.0))
        R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
        return radius


    def set_Rij(self, a, b, radius):
        R = self.Rij
        R[a+b] = R[b+a] = radius


    epsij = {}
    epsij["CC"] = 0.1500 
    epsij["AA"] = epsij["CC"]
    epsij["NN"] = 0.1600
    epsij["OO"] = 0.2000
    epsij["PP"] = 0.2000
    epsij["SS"] = 0.2000
    epsij["HH"] = 0.0200
    epsij["FF"] = 0.0800
    epsij["II"] = 0.5520
    #new ad_types
    epsij["NANA"] = 0.1600
    epsij["OAOA"] = 0.2000
    epsij["SASA"] = 0.2000
    epsij["HDHD"] = 0.0200
    # ad3.05
    epsij["MGMG"] = 0.8750 # Magnesium 
    epsij["MNMN"] = 0.8750 # Manganese
    epsij["ZNZN"] = 0.5500 # Zinc
    epsij["FEFE"] = 0.0100 # Iron
    epsij["MgMg"] = 0.8750 # Magnesium 
    epsij["MnMn"] = 0.8750 # Manganese
    epsij["ZnZn"] = 0.5500 # Zinc
    epsij["FeFe"] = 0.0100 # Iron
    # ad3.05 
    epsij["CACA"] = 0.5500 # Calcium 
    epsij["CLCL"] = 0.2760 # Chlorine 
    epsij["BRBR"] = 0.3890 # Bromine 
    # ad3.05 
    epsij["CaCa"] = 0.5500 # Calcium 
    epsij["ClCl"] = 0.2760 # Chlorine 
    epsij["BrBr"] = 0.3890 # Bromine 



    def get_epsij(self, a, b):
        """Return epsij of a, b atom-type pair

        Add geometric mean of epsij[a+a] and epsij[b+b] if necessary
        """
        e = self.epsij
        well_depth = e.setdefault(a+b, math.sqrt( e[a+a]*e[b+b]))
        e[b+a] = well_depth # enforce symmetry (e[ba] = e[ab])
        return well_depth

        
    def set_epsij(self, a, b, well_depth):
        epsij = self.epsij
        epsij[a+b] = epsij[b+a] = well_depth


    def _f(self, at_a, at_b, dist):
        """ vdw pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 6.
        elm_a = at_a.autodock_element
        elm_b = at_b.autodock_element
        # given the atom types, find epsij and Rij
        epsij = self.get_epsij(elm_a, elm_b)
        Rij = self.get_Rij(elm_a, elm_b)
        if Rij==0.0:
            return 0.0
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = dist**exp_B
        rA = dist**exp_A
        # (MS) FIXME: it happens that rA or rB becomes 0.0 and we get
        # ZeroDivisionError: float division
        try:
            energy = cA/rA - cB/rB
        except ZeroDivisionError:
            return 99999.9
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy


NewVanDerWaals = NewVanDerWaalsRefImpl
#end NewVanDerWaals


#FOR NON-DIRECTIONAL HYDROGENBONDING TERM for internal energy:
class NewHydrogenBonding12_10RefImpl(DistDepPairwiseScorer, HBondVDWSmoothing):
    def __init__(self, ms=None, donors=['HD'], acceptors=['NA','OA','SA']):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictB.setdefault('autodock_element', False)
        if ms is not None:
            self.set_molecular_system(ms)
        pairs = []
        for d in donors:
            for a in acceptors:
                pairs.append(d+a)
                pairs.append(a+d)
        #print "init: pairs =", pairs
        self.pairs_to_evaluate = pairs


    # set up class variables epsij, Rij
    # Access is through the get_ and set_ methods!!
    # dicts will probably move a class of their own

    #for pairs_to_evaluate ONLY
    epsij = {}
    epsij["OAHD"] = epsij["HDOA"] = 5.0
    epsij["NAHD"] = epsij["HDNA"] = 5.0
    epsij["SAHD"] = epsij["HDSA"] = 1.0

    Rij = {}
    Rij["OAHD"] = Rij["HDOA"] = 1.9
    Rij["NAHD"] = Rij["HDNA"] = 1.9
    Rij["SAHD"] = Rij["HDSA"] = 2.5


    def get_Rij(self, a, b, radius):
        R = self.Rij
        radius = R.setdefault(a+b, 0.)
        R[a+b] = R[b+a] = radius
        return radius


    def set_Rij(self, a, b, radius):
        R = self.Rij
        R[a+b] = R[b+a] = radius


    def get_epsij(self, a, b):
        """Return epsij of a, b atom-type pair

        Add geometric mean of epsij[a+a] and epsij[b+b] if necessary
        """
        eps = self.epsij
        well_depth = eps.setdefault(a+b, 0.)
        eps.setdefault(b+a, well_depth)
        return well_depth

        
    def set_epsij(self, a, b, well_depth):
        epsij = self.epsij
        epsij[a+b] = epsij[b+a] = well_depth


    def _f(self, at_a, at_b, dist):
        """ new 12-10 vdw pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 10.
        elm_a = at_a.autodock_element
        elm_b = at_b.autodock_element
        if elm_a + elm_b not in self.pairs_to_evaluate:
            return 0.0
        epsij = self.epsij[elm_a + elm_b]
        Rij = self.Rij[elm_a + elm_b]
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        ##NO SMOOTHING
        ##dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = dist**exp_B
        rA = dist**exp_A
        # (MS) FIXME: it happens that rA or rB becomes 0.0 and we get
        # ZeroDivisionError: float division
        try:
            energy = cA/rA - cB/rB
        except ZeroDivisionError:
            return 99999.9
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy


NewHydrogenBonding12_10 = NewHydrogenBonding12_10RefImpl
#end NewHydrogenBonding12_10



class NewVanDerWaalsHybridWeights(DistDepPairwiseScorer, HBondVDWSmoothing):
    def __init__(self, ms=None, exclude=["OAHD","NAHD","SAHD","HDOA","HDNA","HDSA"], only=[]):
        DistDepPairwiseScorer.__init__(self)
        HBondVDWSmoothing.__init__(self)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA.setdefault('autodock_element', 0)
        self.required_attr_dictB.setdefault('autodock_element', 0)
        #new ad_types
        #self.Rij["OAHD"] = self.Rij["HDOA"] = 0.0
        #self.Rij["NAHD"] = self.Rij["HDNA"] = 0.0
        #self.Rij["SAHD"] = self.Rij["HDSA"] = 0.0
        for pair in exclude:
            self.Rij[pair] = 0.0
        self.score_only = only
        if ms is not None:
            self.set_molecular_system(ms)


    # set up class variables epsij, Rij
    # Access is through the get_ and set_ methods!!
    # dicts will probably move a class of their own

    Rij = {}
    Rij["CC"] = 4.0
    Rij["AA"] = Rij["CC"]
    Rij["NN"] = 3.5
    Rij["OO"] = 3.2
    Rij["PP"] = 4.2
    Rij["SS"] = 4.0
    Rij["HH"] = 2.0
    Rij["FF"] = 3.09
    Rij["II"] = 4.72
    Rij["NANA"] = 3.5
    Rij["OAOA"] = 3.2
    Rij["SASA"] = 4.0
    Rij["HDHD"] = 2.0
    Rij["MGMG"] = 1.3          # Magnesium
    Rij["MNMN"] = 1.3          # Manganese
    Rij["ZNZN"] = 1.48         # Zinc
    Rij["CACA"] = 1.98         # Calcium
    Rij["FEFE"] = 1.3          # Iron
    Rij["CLCL"] = 4.09         # Chlorine
    Rij["BRBR"] = 4.33         # Bromine

    Rij["MgMg"] = 1.3          # Magnesium
    Rij["MnMn"] = 1.3          # Manganese
    Rij["ZnZn"] = 1.48         # Zinc
    Rij["CaCa"] = 1.98         # Calcium
    Rij["FeFe"] = 1.3          # Iron
    Rij["ClCl"] = 4.09         # Chlorine
    Rij["BrBr"] = 4.33         # Bromine


    def get_Rij(self, a, b):
        """Return Rij of a, b atom-type pair
        
        Add arithmetic mean of Rij[a+a] and Rij[b+b] if necessary
        """
        R = self.Rij
        if len(self.score_only):
            if a in self.score_only or b in self.score_only:
                radius = R.setdefault(a+b, ((R[a+a] + R[b+b])/2.0))
                #R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
            else:
                radius = R.setdefault(a+b, (0.0))
                #R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
        else:
            radius = R.setdefault(a+b, ((R[a+a] + R[b+b])/2.0))
            #R[b+a] = radius # enforce symmetry of (r[ba] = r[ab])
        R[b+a] = radius
        return radius


    def set_Rij(self, a, b, radius):
        R = self.Rij
        R[a+b] = R[b+a] = radius


    epsij = {}
    epsij["CC"] = 0.1500
    epsij["AA"] = epsij["CC"] 
    epsij["NN"] = 0.1600
    epsij["OO"] = 0.2000
    epsij["PP"] = 0.2000
    epsij["SS"] = 0.2000
    epsij["HH"] = 0.0200
    epsij["FF"] = 0.0800
    epsij["II"] = 0.5520
    #new ad_types
    epsij["NANA"] = 0.1600
    epsij["OAOA"] = 0.2000
    epsij["SASA"] = 0.2000
    epsij["HDHD"] = 0.0200
    # ad3.05 
    epsij["MGMG"] = 0.8750 # Magnesium 
    epsij["MNMN"] = 0.8750 # Manganese
    epsij["ZNZN"] = 0.5500 # Zinc
    epsij["FEFE"] = 0.0100 # Iron

    epsij["MgMg"] = 0.8750 # Magnesium 
    epsij["MnMn"] = 0.8750 # Manganese
    epsij["ZnZn"] = 0.5500 # Zinc
    epsij["FeFe"] = 0.0100 # Iron
    # ad3.05
    epsij["CaCa"] = 0.5500 # Calcium 
    epsij["ClCl"] = 0.2760 # Chlorine
    epsij["BrBr"] = 0.3890 # Bromine 


    def get_epsij(self, a, b):
        """Return epsij of a, b atom-type pair

        Add geometric mean of epsij[a+a] and epsij[b+b] if necessary
        """
        e = self.epsij
        well_depth = e.setdefault(a+b, math.sqrt( e[a+a]*e[b+b]))
        e[b+a] = well_depth # enforce symmetry (e[ba] = e[ab])
        return well_depth

        
    def set_epsij(self, a, b, well_depth):
        epsij = self.epsij
        epsij[a+b] = epsij[b+a] = well_depth


    def _f(self, at_a, at_b, dist):
        """ vdw pairwise dist dep function
        """
        exp_A = 12.
        exp_B = 6.
        elm_a = at_a.autodock_element
        elm_b = at_b.autodock_element
        if len(self.score_only):
            if elm_a not in self.score_only and elm_b not in self.score_only:
                return 0.0
        # given the atom types, find epsij and Rij
        epsij = self.get_epsij(elm_a, elm_b)
        Rij = self.get_Rij(elm_a, elm_b)
        # now compute the vdw energy
        tmpconst = epsij/(exp_A - exp_B)
        dist = self.smooth_dist(dist, Rij)
        cA = tmpconst * Rij**exp_A * exp_B
        cB = tmpconst * Rij**exp_B * exp_A
        rB = dist**exp_B
        rA = dist**exp_A
        # (MS) FIXME: it happens that rA or rB becomes 0.0 and we get
        # ZeroDivisionError: float division
        try:
            energy = cA/rA - cB/rB
        except ZeroDivisionError:
            return 99999.9
        #return min(EINTCLAMP, cA/rA - cB/rB)
        return energy
#end NewVanDerWaalsHybridWeights



if __name__ == '__main__':
    print "Test are in Tests/test_scorer.py"
    # test_scorer.run_test()
