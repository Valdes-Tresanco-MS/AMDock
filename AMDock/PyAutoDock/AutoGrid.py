## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

#
#
# $Id: AutoGrid.py,v 1.11 2007/07/24 17:30:45 vareille Exp $
#
#

import numpy.oldnumeric as Numeric, os, string

from MolKit.molecule import Atom
from MolKit import Read

from MolecularSystem import MolecularSystem

from AutoDockScorer import AutoGrid305Scorer, AutoDockTermWeights305
from AutoDockScorer import AutoGrid4Scorer, AutoDockTermWeights4
from scorer import WeightedMultiTerm
from electrostatics import Electrostatics
from desolvation import NewDesolvationDesolvMap


class GridMap:
    def __init__(self, entity,
                 npts=[5,5,5], spacing=0.375, center=[0,0,0]):
        self.entity = entity
        self.npts = npts
        self.spacing = spacing
        self.center = center


    def get_entity_list(self):
        """<gen_entities docstring>"""
        npts = self.npts
        sp = self.spacing
        cen = self.center
        ent = self.entity

        
        for z in xrange(-(npts[2]/2), npts[2]/2 + 1):
            for y in xrange(-(npts[1]/2), npts[1]/2 + 1):
                for x in xrange(-(npts[0]/2), npts[0]/2 + 1):
                    ent._coords[ent.conformation] = [x*sp+cen[0],
                                                     y*sp+cen[1],
                                                     z*sp+cen[2]]
                    yield ent


    def get_entity(self):
        """returns the entity supplied to the constructor"""
        return self.entity

# GridMap




class AutoGrid:

    at_vols = { 'C' : 12.77, 
                'A' : 10.80}

    
    def __init__(self, receptor, 
                 atom_types=['A', 'C', 'H', 'N', 'O', 'S'], 
                 npts=[5, 5, 5], spacing=0.375, center=[0., 0., 0.]):

        # we expect the receptor parameter to be a MolKit.Molecule
        # or some such instance with an allAtoms attribute
        assert( hasattr( receptor, 'allAtoms'))
        self.receptor = receptor

        # these are atom_types of the ligand for which maps will be written
        self.atom_types = atom_types

        # make the single atom that will traverse the grid
        self.atom = self._create_atom(atom_types[0])

        # create the GridMap
        self.grid_map = GridMap(self.atom, npts, spacing, center)

                
        # create molecular system
        self.ms = MolecularSystem()
        # (the receptor must be the first molecule in the configuration)
        self.receptor_ix = self.ms.add_entities( self.receptor.allAtoms )

        # add the grid generator to the ms as the 'second molecule'
        self.grid_map_ix = self.ms.add_entities( self.grid_map )

        # that is it for the molecular system for now. later when
        # we write the maps the grid_map's atom attributes
        # (autodock_element and AtVol) must be set for each atom map.

        #make this a separate step so that it can be overridden
        self.setup_scorer()


    def setup_scorer(self):

        # construct atom_map scorer...
        self.atom_map_scorer = AutoGrid305Scorer()
        self.atom_map_scorer.set_molecular_system(self.ms)
        
        # ... and electrostatics scorer
        self.estat_map_scorer = WeightedMultiTerm()
        self.estat_map_scorer.add_term(Electrostatics(), 
                                       AutoDockTermWeights305().estat_weight)
        self.estat_map_scorer.set_molecular_system(self.ms)


    def _create_atom(self, atom_type):
        """Simple, private helper function for __init__
        """
        element = atom_type
        name = element + str(0)
        
        at = Atom(name=name, chemicalElement=element)

        at._charges = {'gridmap': 1.0}
        at.chargeSet = 'gridmap'
        at.number = 1
        at._coords = [[0., 0., 0.]]
        at.conformation = 0

        #these 2 would change between maps:
        at.autodock_element = element
        at.AtVol = self.at_vols.get(element, 0.0)
        #print "set AtVol to", at.AtVol

        return at


    def write_maps(self, filename=None):
        # now create the atom maps
        for element in self.atom_types:
            # set atom.element to the element
            self.atom.element = element
            self.atom.autodock_element = element 
            self.atom.AtVol = self.at_vols.get(element, 0.0)
            
            # score it
            score_array = self.atom_map_scorer.get_score_array()
            # create filename and write it
            filename = self.receptor.name + "." + element + ".map"
            self.write_grid_map(score_array, filename)


        # create the electrostatics map
        score_array = self.estat_map_scorer.get_score_array()
        # create filename and write it
        filename = self.receptor.name + ".e.map"
        self.write_grid_map(score_array, filename)

        # now write the fld file
        filename = self.receptor.name + ".maps.fld"
        self.write_maps_fld(filename)

        # now write the xyz file
        filename = self.receptor.name + ".maps.xyz"
        self.write_xyz_file(filename)


    def set_grid_map_center(self, center):
        self.grid_map.center = center
        self.ms.clear_dist_mat(self.grid_map_ix)
        

    def set_grid_map_npts(self, npts):
        self.grid_map.npts = npts
        self.ms.clear_dist_mat(self.grid_map_ix)


    def set_grid_map_spacing(self, spacing):
        self.grid_map.spacing = spacing
        self.ms.clear_dist_mat(self.grid_map_ix)


    def write_grid_map(self, score_array, filename):
        stem = string.split(os.path.basename(filename), '.')[0]
        # open and write the file
        fptr = open(filename, 'w')

        # line 1:
        ostr = "GRID_PARAMETER_FILE " + stem + ".gpf\n"
        fptr.write(ostr)

        # line 2:
        ostr = "GRID_DATA_FILE " + stem + ".maps.fld\n"
        fptr.write(ostr)

        # line 3:
        ostr = "MACROMOLECULE " + stem + ".pdbqs\n"
        fptr.write(ostr)

        # line 4:
        ostr = "SPACING " + str(self.grid_map.spacing) + "\n"
        fptr.write(ostr)

        # line 5:
        ostr = "NELEMENTS %d %d %d\n" % tuple(self.grid_map.npts)
        fptr.write(ostr)

        # line 6:
        ostr = "CENTER %f %f %f\n" % tuple(self.grid_map.center)
        fptr.write(ostr)

        # now write the values after
        # summing the receptor atom energies for each grid point
        for value in Numeric.add.reduce(score_array):
            ostr = "%.3f\n" % (value)
            fptr.write(ostr)

        # all done...
        fptr.close()
    


    def write_xyz_file(self, filename=None):
        """AutoDock305 and AutoDock4 may require this xyz field file
        """
        xpts, ypts,zpts = self.grid_map.npts
        
        spacing = self.grid_map.spacing
        x_extent = int(xpts/2) * spacing 
        y_extent = int(ypts/2) * spacing
        z_extent = int(zpts/2) * spacing

        xcen, ycen, zcen = self.grid_map.center

        if filename is None:
            filename = self.receptor.name + '.maps.xyz'

        fptr = open(filename, 'w')
        ostr =    "%5.3f %5.3f\n" %(xcen-x_extent, xcen+x_extent) 
        fptr.write(ostr)
        ostr =    "%5.3f %5.3f\n" %(ycen-y_extent, ycen+y_extent) 
        fptr.write(ostr)
        ostr =    "%5.3f %5.3f\n" %(zcen-z_extent, zcen+z_extent) 
        fptr.write(ostr)

        fptr.close()


    def write_maps_fld(self, filename=None):
        """AutoDock305 and AutoDock4 require this maps fld file
        """
        if filename is None:
            filename = self.receptor.name + '.maps.fld'
        stem = string.split(os.path.basename(filename), '.')[0]
        # open and write the file
        fptr = open(filename, 'w')

        # lines 1 + 2:
        ostr = "# AVS field file\n#\n"
        fptr.write(ostr)

        # lines 3 + 4:
        ostr = "# AutoDock Atomic Affinity and Electrostatic Grids\n#\n"
        fptr.write(ostr)

        # lines 5 + 6:
        ostr = "# Created by AutoGrid.py\n#\n"
        fptr.write(ostr)

        # line 7 spacing info
        ostr = "#SPACING %5.3f \n" %self.grid_map.spacing
        fptr.write(ostr)

        # line 8 npts info
        ostr = "#NELEMENTS %d %d %d\n" % tuple(self.grid_map.npts)
        fptr.write(ostr)

        # line 9:
        ostr = "#CENTER %f %f %f\n" % tuple(self.grid_map.center)
        fptr.write(ostr)

        # line 10:
        ostr = "#MACROMOLECULE %s\n" % self.receptor.name
        fptr.write(ostr)

        # lines 11+12:
        #IS THIS CORRECT//REQUIRED???
        gpffilename = self.receptor.name + '.gpf'
        ostr = "#GRID_PARAMETER_FILE %s\n#\n" % gpffilename
        fptr.write(ostr)

        #avs stuff
        # line 13:
        ostr = "ndim=3\t\t\t# number of dimensions in the field\n"
        fptr.write(ostr)

        # lines 14-16:
        xnpts = self.grid_map.npts[0]
        if xnpts%2==0: xnpts = xnpts+1
        ynpts = self.grid_map.npts[1]
        if ynpts%2==0: ynpts = ynpts+1
        znpts = self.grid_map.npts[1]
        if znpts%2==0: znpts = znpts+1
        ostr = "dim1=%d			# number of x-elements\n" %xnpts
        fptr.write(ostr)
        ostr = "dim2=%d			# number of y-elements\n" %ynpts
        fptr.write(ostr)
        ostr = "dim3=%d			# number of z-elements\n" %znpts
        fptr.write(ostr)

        # line 17:
        ostr = "nspace=3		# number of physical coordinates per point\n"
        fptr.write(ostr)

        # line 18:
        veclen = len(self.atom_types) + 1  #atommaps + estat map
        ostr = "veclen=%d		# number of affinity values at each point\n" %veclen
        fptr.write(ostr)

        #lines 19 + 20:
        ostr = "data=float		# data type (byte, integer, float, double)\nfield=uniform		# field type (uniform, rectilinear, irregular)\n"
        fptr.write(ostr)

        #lines 21-23:
        xyzfilename = self.receptor.name + '.maps.xyz'
        for i in range(3):
            ostr = "coord %d file=%s.maps.xyz filetype=ascii offset=%d\n" %(i+1, self.receptor.name, i*2)
            fptr.write(ostr)

        #lines 23-23+num_atom_maps:
        for ix, t in enumerate(self.atom_types):
            ostr = "label=%s-affinity\t# component label for variable %d\n"%(t,ix+1) 
            fptr.write(ostr)

        #output electrostatics label 
        ostr = "label=Electrostatics\t# component label for variable %d\n"%(ix+1) 
        fptr.write(ostr)

        # comment lines:
        ostr = "#\n# location of affinity grid files and how to read them\n#\n"
        fptr.write(ostr)
        
        #more lines for each map
        for ix, t in enumerate(self.atom_types):
            mapfilename = self.receptor.name + '.' + t + '.map'
            ostr = "variable %d file=%s filetype=ascii skip=6\n"%(ix+1,mapfilename) 
            fptr.write(ostr)
        e_mapfilename = self.receptor.name + '.e.map'
        ostr = "variable %d file=%s filetype=ascii skip=6\n"%(ix+2,e_mapfilename) 
        fptr.write(ostr)

        fptr.close()

# AutoGrid



class AutoGrid4(AutoGrid):

    
    def __init__( self, receptor, atom_types=['A', 'C', 'HD', 'NA', 'OA', 'SA'], 
                 npts=[5, 5, 5], spacing=0.375, center=[0., 0., 0.]):
        AutoGrid.__init__(self, receptor, atom_types, npts, spacing, center)


    def setup_scorer(self):
        # construct atom_map scorer...
        #lenB is required for newHydrogenBonding term
        npts = self.grid_map.npts
        self.ms.lenB = npts[0]*npts[1]*npts[2]
        self.atom_map_scorer = AutoGrid4Scorer()
        self.atom_map_scorer.set_molecular_system(self.ms)
        
        # ... and newdesolvationdesolvmap scorer
        self.desolv_map_scorer = WeightedMultiTerm()
        self.desolv_map_scorer.add_term(NewDesolvationDesolvMap(), 
                                       AutoDockTermWeights4().dsolv_weight)
        self.desolv_map_scorer.set_molecular_system(self.ms)
        
        # ... and electrostatics scorer
        self.estat_map_scorer = WeightedMultiTerm()
        self.estat_map_scorer.add_term(Electrostatics(), 
                                       AutoDockTermWeights4().estat_weight)
        self.estat_map_scorer.set_molecular_system(self.ms)


    def _create_atom(self, atom_type):
        """Simple, private helper function for __init__
        """
        element = atom_type
        name = element + str(0)
        
        at = Atom(name=name, chemicalElement=element)

        at._charges = {'gridmap': 1.0}
        at.chargeSet = 'gridmap'
        at.number = 1
        at._coords = [[0., 0., 0.]]
        at.conformation = 0

        #these 2 would change between maps:
        at.autodock_element = element
        #volumes are in the scorer
        #at.AtVol = self.at_vols.get(element, 0.0)
        #print "set AtVol to", at.AtVol

        return at


    def write_maps(self, filename=None):
        # now create the atom maps
        for element in self.atom_types:
            # set atom.element to the element
            self.atom.element = element
            self.atom.autodock_element = element 
            #self.atom.AtVol = self.at_vols.get(element, 0.0)
            
            # score it
            score_array = self.atom_map_scorer.get_score_array()
            # create filename and write it
            filename = self.receptor.name + "." + element + ".map"
            self.write_grid_map(score_array, filename)


        # create the desolvation map
        score_array = self.desolv_map_scorer.get_score_array()
        # create filename and write it
        filename = self.receptor.name + ".d.map"
        self.write_grid_map(score_array, filename)


        # create the electrostatics map
        score_array = self.estat_map_scorer.get_score_array()
        # create filename and write it
        filename = self.receptor.name + ".e.map"
        self.write_grid_map(score_array, filename)

        # now write the fld file
        filename = self.receptor.name + ".maps.fld"
        self.write_maps_fld(filename)

        # now write the xyz file
        filename = self.receptor.name + ".maps.xyz"
        self.write_xyz_file(filename)


# AutoGrid4



if __name__ == '__main__':
    print "Test are in Tests/test_AutoGrid.py"
