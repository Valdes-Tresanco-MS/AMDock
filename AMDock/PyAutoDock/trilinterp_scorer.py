## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: Ruth Huey, William Lindstrom
#
# Copyright: A. Olson TSRI 2006
#
#############################################################################

#
# $Id: trilinterp_scorer.py,v 1.7 2007/07/24 17:30:45 vareille Exp $
#

import numpy.oldnumeric as Numeric

from PyAutoDock.scorer import ScoringStrategy
from PyAutoDock.MolecularSystem import MolecularSystem



class TrilinterpScorer(ScoringStrategy):
    def __init__(self, stem, atomtypes, ms=None, value_outside_grid=1000000.,
                    atoms_to_ignore=[], readMaps=True):
        """
        based on AD4 scoring function:
        stem and atomtypes list specify filenames for maps
        value_outside_grid is energy penalty for pts outside box
        atoms_to_ignore are assigned 0.0 energy: specifically
        added to avoid huge energies from atoms bonded to flexible residues
        """
        ScoringStrategy.__init__(self, None)
        self.stem = stem
        self.atomtypes = atomtypes
        self.map_data = {}
        #eg: stem = 'hsg1', atomtypes= ['C','A','HD','N','S']
        if readMaps:
            self.read_maps(stem, atomtypes)
        if ms is not None:
            self.set_molecular_system(ms)
        # add the required attributes of this subclass to the dict
        self.required_attr_dictA = {}
        self.required_attr_dictA.setdefault('coords', False)
        self.required_attr_dictA.setdefault('charge', False)
        self.required_attr_dictA.setdefault('autodock_element', False)
        self.required_attr_dictB = {}
        self.value_outside_grid = value_outside_grid
        self.atoms_to_ignore = atoms_to_ignore

        
##     def set_map(self, map_type, grid_obj): 
##         """
##         eg map_type=HD, grid_obj, instance of Pmv.Grid class
                      
##         """
##         self.grid_obj = grid_obj
##         cen = grid_obj.CENTER
##         spacing = grid_obj.SPACING
##         npts = grid_obj.NELEMENTS
##         self.inv_spacing = 1.0/spacing
##         #setup the lowvalues for each dimension
##         #assume even number of pts?
##         x_extent = spacing * (npts[0]-1)
##         self.map_data[map_type] = grid_obj.array
##         self.x_low = cen[0] - x_extent/2.
##         self.x_high = cen[0] + x_extent/2.
##         y_extent = spacing * (npts[1]-1)
##         self.y_low = cen[1] - y_extent/2.
##         self.y_high = cen[1] + y_extent/2.
##         z_extent = spacing * (npts[2]-1)
##         self.z_low = cen[2] - z_extent/2.
##         self.z_high = cen[2] + z_extent/2.
##         if not hasattr(grid_obj,'scorers'):
##             grid_obj.scorers = []
##         grid_obj.scorers.append(self)
##         print "x_low,y_low,z_low=", self.x_low, self.y_low, self.z_low
##         print "x_high,y_high,z_high=", self.x_high, self.y_high, self.z_high


    def add_maps(self,stem,atomtypes):
        """
        read a map for each specified atom type
        stem: string
        atomtypes: []  i.e ['C','HD']
        """
        for t in atomtypes:
            filename = "%s.%s.map" %(stem, t)
            self.read_map(filename)

        return True
        
    def read_maps(self, stem, atomtypes):
        """
        read one map for each specified atom type plus 
        desolvation and electrostatics maps...
        """

        self.add_maps(stem, atomtypes)

        #next read the desolvation map
        dsolvmapname = "%s.d.map" %(stem)
        self.read_map(dsolvmapname)
        #finally read the electrostatics map
        elecmapname = "%s.e.map" %(stem)
        self.read_map(elecmapname)


    def read_map(self, filename):
        mapfileptr = open(filename)
        maplines = mapfileptr.readlines()
        gpf = maplines[0].split()[1]
        grid_data_file = maplines[1].split()[1]
        macromolecule = maplines[2].split()[1]
        spacing = self.spacing = float(maplines[3].split()[1])
        npts = self.npts = map(int, maplines[4].split()[1:])
        for i in range(3):
            if npts[i]%2==0: npts[i]+=1 
        cen = self.cen = map(float, maplines[5].split()[1:])
        keys = ['gpf','grid_data_file','macromolecule','spacing','npts','cen']
        values= [gpf,grid_data_file,macromolecule,spacing,npts,cen]
        #make sure all maps have the same info
        for k, new_val in zip(keys, values):
            old_val = getattr(self, k, new_val)  
            assert old_val== new_val
        self.inv_spacing = 1.0/self.spacing
        #setup the lowvalues for each dimension
        #assume even number of pts?
        x_extent = spacing * (npts[0]-1)
        self.x_low = cen[0] - x_extent/2.
        self.x_high = cen[0] + x_extent/2.
        y_extent = spacing * (npts[1]-1)
        self.y_low = cen[1] - y_extent/2.
        self.y_high = cen[1] + y_extent/2.
        z_extent = spacing * (npts[2]-1)
        self.z_low = cen[2] - z_extent/2.
        self.z_high = cen[2] + z_extent/2.
        ##print "x_low,y_low,z_low=", self.x_low, self.y_low, self.z_low
        #parse the data
        data = []
        for line in maplines[6:]:
            data.append(float(line[:-1]))
        #keep data for this map
        map_type = filename.split('.')[1]
        data_array = Numeric.array(data)
        data_array.shape = (npts[0], npts[1], npts[2])
        self.map_data[map_type] = data_array


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

        # check the required attribute for both subsets before going on
        listA = []
        for k,v in self.required_attr_dictA.items():
            if not v:
                listA.append(k)
                self.required_attr_dictA[k] = True
        ms.check_required_attributes( ms.configuration[0], listA)
        # now set the molecular system
        self.ms = ms
        for at in self.atoms_to_ignore:
            at.ignore = 1

        # check that all the atom type in the ligan have a corresponding map loaded
        # get uniq atoms type in ligand
        atom_type = {}
        ligand = ms.get_entities(ms.configuration[0])
        for x in ligand:
            atom_type[x.autodock_element] =''

        for type in atom_type.keys():
            if type not in self.map_data.keys():
                # try to load map from previously define stem
                status = self.add_maps(self.stem,[type])
                if not status:raise RuntimeError("grid map missing for atomtype %s"%type)
            

    def get_score_array(self):
        array = []
        for at_a in self.ms.get_entities(self.ms.configuration[0]):
            if hasattr(at_a, 'ignore'):
                atom_score = 0
            else:
                atom_score = self._f(at_a)
            array.append(atom_score)
        self.array = Numeric.array(array)
        return self.array
            

    def get_score(self):
        if self.ms is None:
            raise RuntimeError("no molecular system available in scorer")
        array = self.get_score_array()
        return Numeric.add.reduce(array)


    def is_out_grid_info(self, x, y,z):
        if x<self.x_low or x>self.x_high or y<self.y_low or y>self.y_high or z<self.z_low or z>self.z_high :
            return True


    def _f_1map(self, at1):
        # simple f using only 1 map for scoring
        # for example, one built from sum of coordinates
        x, y, z = at1.coords
        if (self.is_out_grid_info(x,y,z)):
            return self.value_outside_grid

        inv_spacing = self.inv_spacing
        ##print "inv_spacing=", inv_spacing

        #sample pt [0,0,0], x_low=y_low=z_low=-20, spacing=.25
        u = (x - self.x_low)*inv_spacing # 0- -20*4 = 80
        u0 = int(u)  #80
        u1 = u0 + 1  #81
        p0u = u - float(u0) #-1
        p1u = 1.0 - p0u  #0.9
        ##print "u=",u, " u0=", u0, " u1=", u1, " p0u=", p0u,  ' p1u=', p1u

        v = (y - self.y_low)*inv_spacing
        v0 = int(v)
        v1 = v0 + 1
        p0v = v - float(v0)
        p1v = 1.0 - p0v
        ##print "v=",v, " v0=", v0, " v1=", v1, " p0v=", p0v,  ' p1v=', p1v

        w = (z - self.z_low)*inv_spacing
        w0 = int(w)
        w1 = w0 + 1
        p0w = w - float(w0)
        p1w = 1.0 - p0w
        ##print "w=",w, " w0=", w0, " w1=", w1, " p0w=", p0w,  ' p1w=', p1w

        e = m = d = 0.0

        at_data = self.map_data[at1.autodock_element]

        m += p1u * p1v * p1w * at_data[w0][v0][u0]
        m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        return  m 
        


    #def _f(self, at1, at2): scorers which inherit from pairwise need two atom input
    def _f(self, at1):
        #find index into list of data for this atoms coords
        x, y, z = at1.coords

        if (self.is_out_grid_info(x,y,z)):
            return self.value_outside_grid
        inv_spacing = self.inv_spacing

        u = (x - self.x_low)*inv_spacing
        u0 = int(u)
        u1 = u0 + 1
        p0u = u - float(u0)
        p1u = 1.0 - p0u
        #print "u=",u, " u0=", u0, " u1=", u1, " p0u=", p0u,  ' p1u=', p1u

        v = (y - self.y_low)*inv_spacing
        v0 = int(v)
        v1 = v0 + 1
        p0v = v - float(v0)
        p1v = 1.0 - p0v
        #print "v=",v, " v0=", v0, " v1=", v1, " p0v=", p0v,  ' p1v=', p1v

        w = (z - self.z_low)*inv_spacing
        w0 = int(w)
        w1 = w0 + 1
        p0w = w - float(w0)
        p1w = 1.0 - p0w
        #print "w=",w, " w0=", w0, " w1=", w1, " p0w=", p0w,  ' p1w=', p1w

        #add code to deal with pts outside grid and on edges

        e = m = d = 0.0

        #look up this atom in the appropriate map
        at_data = self.map_data[at1.autodock_element]
        #desolvation energy map
        d_data = self.map_data['d']
        #electrostatics energy map
        e_data = self.map_data['e']

        #e += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][ElecMap];
        e += p1u * p1v * p1w * e_data[w0][v0][u0] 
        #m += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][AtomType];
        ##debug only##m += p1u * p1v * p1w * at_data[w0][v0][u0]
        m += p1u * p1v * p1w * at_data[w0][v0][u0]
        #d += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][DesolvMap];
        d += p1u * p1v * p1w * d_data[w0][v0][ u0 ]

        #d += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][DesolvMap];
        d += p0u * p1v * p1w * d_data[ w0 ][ v0 ][ u1 ]
        #m += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][AtomType];
        ##debug only##m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        #e += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][ElecMap];
        e += p0u * p1v * p1w * e_data[ w0 ][ v0 ][ u1 ]

        #e += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][ElecMap];
        e += p1u * p0v * p1w * e_data[ w0 ][ v1 ][ u0 ]
        #m += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][AtomType];
        ##debug only##m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        #d += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][DesolvMap];
        d += p1u * p0v * p1w * d_data[ w0 ][ v1 ][ u0 ]

        #d += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][DesolvMap];
        d += p0u * p0v * p1w * d_data[ w0 ][ v1 ][ u1 ]
        #m += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][AtomType];
        ##debug only##m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        #e += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][ElecMap];
        e += p0u * p0v * p1w * e_data[ w0 ][ v1 ][ u1 ]

        #e += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][ElecMap];
        e += p1u * p1v * p0w * e_data[ w1 ][ v0 ][ u0 ]
        #m += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][AtomType];
        ##debug only##m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        #d += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][DesolvMap];
        d += p1u * p1v * p0w * d_data[ w1 ][ v0 ][ u0 ]

        #d += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][DesolvMap];
        d += p0u * p1v * p0w * d_data[ w1 ][ v0 ][ u1 ]
        #m += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][AtomType];
        ##debug only##m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        #e += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][ElecMap];
        e += p0u * p1v * p0w * e_data[ w1 ][ v0 ][ u1 ]

        #e += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][ElecMap];
        e += p1u * p0v * p0w * e_data[ w1 ][ v1 ][ u0 ]
        #m += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][AtomType];
        ##debug only## m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        #d += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][DesolvMap];
        d += p1u * p0v * p0w * d_data[ w1 ][ v1 ][ u0 ]

        #d += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][DesolvMap];
        d += p0u * p0v * p0w * d_data[ w1 ][ v1 ][ u1 ]
        #m += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][AtomType];
        ##debug only##m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        #e += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][ElecMap];
        e += p0u * p0v * p0w * e_data[ w1 ][ v1 ][ u1 ]
        
        charge = at1.charge
        return e*charge + m + d*abs(charge)
        


class TrilinterpScorer_AD3(TrilinterpScorer):
    def __init__(self, stem, atomtypes, ms=None, value_outside_grid=1000000.,
                    atoms_to_ignore=[]):
        """
        stem and atomtypes list specify filenames for maps
        """
        TrilinterpScorer.__init__(self, stem, atomtypes, ms, value_outside_grid, 
                                    atoms_to_ignore)


    def read_maps(self, stem, atomtypes):
        for t in atomtypes:
            filename = "%s.%s.map" %(stem, t)
            self.read_map(filename)
        #dsolvmapname = "%s.d.map" %(stem)
        #self.read_map(dsolvmapname)
        elecmapname = "%s.e.map" %(stem)
        self.read_map(elecmapname)



    def _f_1map(self, at1):
        # simple f using only 1 map for scoring
        # for example, one built from sum of coordinates
        x, y, z = at1.coords
        if (self.is_out_grid_info(x,y,z)):
            return self.value_outside_grid

        inv_spacing = self.inv_spacing
        ##print "inv_spacing=", inv_spacing

        #sample pt [0,0,0], x_low=y_low=z_low=-20, spacing=.25
        u = (x - self.x_low)*inv_spacing # 0- -20*4 = 80
        u0 = int(u)  #80
        u1 = u0 + 1  #81
        p0u = u - float(u0) #-1
        p1u = 1.0 - p0u  #0.9
        ##print "u=",u, " u0=", u0, " u1=", u1, " p0u=", p0u,  ' p1u=', p1u

        v = (y - self.y_low)*inv_spacing
        v0 = int(v)
        v1 = v0 + 1
        p0v = v - float(v0)
        p1v = 1.0 - p0v
        ##print "v=",v, " v0=", v0, " v1=", v1, " p0v=", p0v,  ' p1v=', p1v

        w = (z - self.z_low)*inv_spacing
        w0 = int(w)
        w1 = w0 + 1
        p0w = w - float(w0)
        p1w = 1.0 - p0w
        ##print "w=",w, " w0=", w0, " w1=", w1, " p0w=", p0w,  ' p1w=', p1w

        e = m = d = 0.0

        at_data = self.map_data[at1.autodock_element]

        m += p1u * p1v * p1w * at_data[w0][v0][u0]
        m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        return  m 
        


    def _f(self, at1):
        #find index into list of data for this atoms coords
        x, y, z = at1.coords
        if (self.is_out_grid_info(x,y,z)):
            return self.value_outside_grid
        inv_spacing = self.inv_spacing

        u = (x - self.x_low)*inv_spacing
        u0 = int(u)
        u1 = u0 + 1
        p0u = u - float(u0)
        p1u = 1.0 - p0u
        #print "u=",u, " u0=", u0, " u1=", u1, " p0u=", p0u,  ' p1u=', p1u

        v = (y - self.y_low)*inv_spacing
        v0 = int(v)
        v1 = v0 + 1
        p0v = v - float(v0)
        p1v = 1.0 - p0v
        #print "v=",v, " v0=", v0, " v1=", v1, " p0v=", p0v,  ' p1v=', p1v

        w = (z - self.z_low)*inv_spacing
        w0 = int(w)
        w1 = w0 + 1
        p0w = w - float(w0)
        p1w = 1.0 - p0w
        #print "w=",w, " w0=", w0, " w1=", w1, " p0w=", p0w,  ' p1w=', p1w

        #add code to deal with pts outside grid and on edges

        e = m  = 0.0
        #e = m = d = 0.0

        #look up this atom in the appropriate map
        at_data = self.map_data[at1.autodock_element]
        ##desolvation energy map
        #d_data = self.map_data['d']
        #electrostatics energy map
        e_data = self.map_data['e']

        #e += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][ElecMap];
        e += p1u * p1v * p1w * e_data[w0][v0][u0] 
        #m += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][AtomType];
        ##debug only##m += p1u * p1v * p1w * at_data[w0][v0][u0]
        m += p1u * p1v * p1w * at_data[w0][v0][u0]
        ##d += p1u * p1v * p1w * map[ w0 ][ v0 ][ u0 ][DesolvMap];
        #d += p1u * p1v * p1w * d_data[w0][v0][ u0 ]

        ##d += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][DesolvMap];
        #d += p0u * p1v * p1w * d_data[ w0 ][ v0 ][ u1 ]
        #m += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][AtomType];
        ##debug only##m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        m += p0u * p1v * p1w * at_data[ w0 ][ v0 ][ u1 ]
        #e += p0u * p1v * p1w * map[ w0 ][ v0 ][ u1 ][ElecMap];
        e += p0u * p1v * p1w * e_data[ w0 ][ v0 ][ u1 ]

        #e += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][ElecMap];
        e += p1u * p0v * p1w * e_data[ w0 ][ v1 ][ u0 ]
        #m += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][AtomType];
        ##debug only##m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        m += p1u * p0v * p1w * at_data[ w0 ][ v1 ][ u0 ]
        ##d += p1u * p0v * p1w * map[ w0 ][ v1 ][ u0 ][DesolvMap];
        #d += p1u * p0v * p1w * d_data[ w0 ][ v1 ][ u0 ]

        ##d += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][DesolvMap];
        #d += p0u * p0v * p1w * d_data[ w0 ][ v1 ][ u1 ]
        #m += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][AtomType];
        ##debug only##m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        m += p0u * p0v * p1w * at_data[ w0 ][ v1 ][ u1 ]
        #e += p0u * p0v * p1w * map[ w0 ][ v1 ][ u1 ][ElecMap];
        e += p0u * p0v * p1w * e_data[ w0 ][ v1 ][ u1 ]

        #e += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][ElecMap];
        e += p1u * p1v * p0w * e_data[ w1 ][ v0 ][ u0 ]
        #m += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][AtomType];
        ##debug only##m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        m += p1u * p1v * p0w * at_data[ w1 ][ v0 ][ u0 ]
        ##d += p1u * p1v * p0w * map[ w1 ][ v0 ][ u0 ][DesolvMap];
        #d += p1u * p1v * p0w * d_data[ w1 ][ v0 ][ u0 ]

        ##d += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][DesolvMap];
        #d += p0u * p1v * p0w * d_data[ w1 ][ v0 ][ u1 ]
        #m += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][AtomType];
        ##debug only##m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        m += p0u * p1v * p0w * at_data[ w1 ][ v0 ][ u1 ]
        #e += p0u * p1v * p0w * map[ w1 ][ v0 ][ u1 ][ElecMap];
        e += p0u * p1v * p0w * e_data[ w1 ][ v0 ][ u1 ]

        #e += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][ElecMap];
        e += p1u * p0v * p0w * e_data[ w1 ][ v1 ][ u0 ]
        #m += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][AtomType];
        ##debug only## m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        m += p1u * p0v * p0w * at_data[ w1 ][ v1 ][ u0 ]
        ##d += p1u * p0v * p0w * map[ w1 ][ v1 ][ u0 ][DesolvMap];
        #d += p1u * p0v * p0w * d_data[ w1 ][ v1 ][ u0 ]

        ##d += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][DesolvMap];
        #d += p0u * p0v * p0w * d_data[ w1 ][ v1 ][ u1 ]
        #m += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][AtomType];
        ##debug only##m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        m += p0u * p0v * p0w * at_data[ w1 ][ v1 ][ u1 ]
        #e += p0u * p0v * p0w * map[ w1 ][ v1 ][ u1 ][ElecMap];
        e += p0u * p0v * p0w * e_data[ w1 ][ v1 ][ u1 ]
        
        charge = at1.charge
        #return e*charge + m + d*abs(charge)
        return e*charge + m
        


if __name__ == '__main__':
    print 'in main'
    tls = TrilinterpScorer('test', ['C'])
    from MolKit import Read
    m = Read("test.pdb")[0]
    #crds= [4.083,6.527,-3.152], [2.737,6.793,-3.728], [1.900,5.679,-4.323]
    ms = MolecularSystem()
    ms.add_entities(m.allAtoms)
    tls.set_molecular_system(ms)


