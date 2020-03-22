## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

############################################################################
#
# Authors: William Lindstrom, Ruth Huey
#
# Copyright: A. Olson TSRI 2004
#
#############################################################################

#
# $Id: MolecularSystem.py,v 1.9 2008/11/21 20:02:00 vareille Exp $
#

from MolKit.molecule import AtomSet, Atom
from MolecularSystemAdapter import Adapters
import numpy.oldnumeric as Numeric
from math import sqrt
import types


class AbstractMolecularSystem:
    """This class defines the interface that a MolecularSystem must support
for use with a Scorer or other object(s). This class maintains a list of
sets of entities (like Atoms).

The get_supported_attributes method returns the list of attributes that
each Entity supports.

A distance matrix is maintained pairwise by set and pairwise by entities
within the set. NB: is actually the distance, **not** distance-squared.
The reason for this is that for clients (like WeightedMultiTerm scorers)
who must get_dist_mat repeatedly, forcing them to take the sqrt for each
term is a false economy.

An index is returned when adding a set of entities (by the add_entities method).
This index for an entity set can also be found using the get_entity_set_index method.
The molecular system attribute configuration is a 2-tuple of validated
entity_set_index. In its use, the Autodock scorer uses the first as the Receptor
and second as the Ligand.


This class is intended to abstract any number of underlying molecular
representations such as MolKit, mmLib, MMTK, or just a PDB file. The
underlying molecular representation is abstracted as a list of entities
which support the 'supported_attributes'. So, for instance, if your molecular
representation doesn't have charges, its abstraction as a specialized
implementation of this interface (ie the subclass of MolecularSystemBase)
may have to calculate per entity charges.
"""
    
    def __init__(self): pass
    def add_entities(self, entity_set, coords_access_func=None): pass
    def get_entity_set_index(self, entity_set): pass
    def set_coords(self, entity_set_index, coords): pass
    
    def get_dist_mat(self, ix, jx): pass
    def clear_dist_mat(self, ix): pass

    def get_supported_attributes(self): pass
    def check_required_attributes(self, entity_set_index, attribute_list): pass
    
    # @@ do we want to support the following interface??
    def get_coords(self, entity_set_index): pass
    
    # @@ or do we want to support the following interface??
    def get_entities(self, entity_set_num): pass

    def set_configuration(self, ix=None, jx=None ): pass
    

    
class MolecularSystem(AbstractMolecularSystem):
    """concrete subclass implementation of AbstractMolecularSystem

    """
    def __init__(self, e_set=None, coords_access_func=None):
        AbstractMolecularSystem.__init__(self)
        self.entity_sets = []
        self._dist_mats = {}
        # key is entity_set_index: values is dict
        # with key second entity_set_index, value distance mat
        # _dist_mat holds the square of distances between pairs of
        # entities, Distance matrices get computed only when needed
        self.configuration = (None, None)
        self.coords_access_func_list = []
        if e_set is not None:
            self.add_entities(e_set, coords_access_func)
            # single entity_set results in configuration of (0,0)
            # self.configuration = (0, None)


    def get_entity_set_index(self, entity_set):
        return self.entity_sets.index(entity_set)


    def _validate_entity_set_index(self, entity_set_ix):
        assert (entity_set_ix < len(self.entity_sets)), \
               "Invalid entity_set_index: %d; only %d entity_sets." % \
               (entity_set_ix, len(self.entity_sets) )

        
    def get_supported_attributes(self):
        raise NotImplementedError

    # for check_required_attributes
    # the hydrogen bonding term has the required attr of bonds
    # for subsetA, so when we implement this make sure that
    # 1. bonds is on the attribute_list when Hbonding is involved
    # 2. that subsetA does have bonds (or build them!)
    #
    # this also raises the issue that not all atom_sets need all attributes
    # to support a specific scorer term.
    #
    # also, for desolvation subsetA needs AtVols

    def check_required_attributes(self, entity_set_index, attribute_list):
        """Check that all the elements of the given entity_set have all
the attributes in the attribute_list.
        """
        # get_entities will validate entity_set_index
        entities = self.get_entities( entity_set_index)

        if type(entities) == types.GeneratorType:
            # @@ figure out how to check generator attributes !!
            return

        # check each attribute
        typeList = [types.ListType, types.DictType]#, types.InstanceType]
        from mglutil.util.misc import isInstance
        for attr in attribute_list:
            # get returns the subset of entities
            # for which the expression is true
            ents = entities.get( lambda x: hasattr(x, attr))
            if ents==None or len(ents)!=len(entities):
                raise AttributeError, \
                      "All Entities do not have required Entity attribute (%s) " % attr
            ent0 = entities[0]
            if type(getattr(ent0, attr)) in typeList \
              or isInstance(getattr(ent0, attr)) is True:
                if len(getattr(ent0, attr))==0:
                    raise ValueError, \
                          "Required Entity attribute (%s) has zero length" % attr


    def _compute_distance_matrix(self, ix, jx):
        """Compute the distance matrix for the given sets

This method should be called from within the class by get_dist_mat
which knows when it's really necessary.
        """
        # straight forward distance matrix calculation
        mat = []
        for c1 in self.get_coords(ix):
            l = []
            cx, cy, cz = c1
            mat.append(l)
            for c2 in self.get_coords(jx):
                c2x, c2y, c2z = c2
                d = cx-c2x, cy-c2y, cz-c2z
                l.append(sqrt( d[0]*d[0]+d[1]*d[1]+d[2]*d[2]) )
        return mat


    def check_distance_cutoff(self, ix, jx, cutoff):
        """check if a distance in the distance matrix for the specified sets
is below a user specified cutoff.

If the distance matrix does not exist if is computed up to the first encounter
of a distance below the cutoff. If such a distance is encountered it is
returned. If the matrix exists the minimum distance is returned if it is below
the cutoff. If distance are all above the cutoff, None is returned.
"""
        mat = self._dist_mats[ix][jx]
        if mat is None:
            mat = self._dist_mats[jx][ix]

        result = None
        if mat is None:
            mat = []
            for e1 in self.get_entities(ix):
                l = []
                cx, cy, cz = e1.coords
                mat.append(l)
                for e2 in self.get_entities(jx):
                    c2x, c2y, c2z = e2.coords
                    d = cx-c2x, cy-c2y, cz-c2z
                    dist = sqrt( d[0]*d[0]+d[1]*d[1]+d[2]*d[2])
                    if dist < cutoff:
                        return dist
                    l.append( dist)
            #if the whole dist matrix is ok, save it
            self._dist_mats[ix][jx] = mat
        else:
            mini = min( map( min, mat))
            if mini < cutoff:
                result = mini
        return result
    

    def get_dist_mat(self, ix, jx):
        """return the distance matrix for the given two sets
        """
        mat = self._dist_mats[ix][jx]
        tmat = self._dist_mats[jx][ix]
        
        if not mat:
            if tmat:
                # we just transpose
                #mat = Numeric.swapaxes(Numeric.array(tmat), 0, 1).tolist()
                mat = [] #eg: 3x4->4x3
                for j in xrange(len(tmat[0])):
                    mat.append([])
                    for i in xrange(len(tmat)):
                        mat[j].append(tmat[i][j])
            else:
                # we must compute
                mat = self._compute_distance_matrix(ix,jx)
            self._dist_mats[ix][jx] = mat
        return mat


    def clear_dist_mat(self, ix):
        """clear all distance-squared matrices for the given entity_set
        """
        
        # first clear all the pairs where entity_set is the first key
        for set in self._dist_mats[ix].keys():
            self._dist_mats[ix][set] = None

        # now clear all matrices where entity_set is the second key
        for set in self._dist_mats.keys():
            self._dist_mats[set][ix] = None


    def set_configuration(self, ix=None, jx=None ):
        """For now this is a 2-tuple of entity_set_index that describes
for a scorer which two entity sets are  being considered with respect to
one another.
        """
        if ix is not None:
            self._validate_entity_set_index(ix)
            self.configuration = tuple( [ix, self.configuration[1]] )
        if jx is not None:
            self._validate_entity_set_index(jx)
            self.configuration = tuple( [self.configuration[0], jx] )

    
    def add_entities(self, entity_set, coords_access_func=None):
        """add a MolKit.EntitySet to the MolecularSystem
        
Returns the entity_set_num for the new EntitySet. First two calls to
add_entities set the configuration to use those EntitySets.
        """
        entity_set_ix =  len(self.entity_sets)

        # initialize the dictionary of distance matricies for this set
        self._dist_mats[entity_set_ix] = {}

        # create an adapter for this entity_set ...
        adapter = Adapters[str(entity_set.__class__)](entity_set)
#        adapter = MolecularSystemAdapter( entity_set)
        # ... and add it to the entity_sets list
        self.entity_sets.append(adapter)
        
        # add the coords_access_func
        self.coords_access_func_list.append(coords_access_func)
        
        # create a new dict for every set vs. this one
        for ix, set in enumerate(self.entity_sets):
            self._dist_mats[ix][entity_set_ix] = None
            self._dist_mats[entity_set_ix][ix] = None

        # set the configuration (only on the first two calls)
        if entity_set_ix == 0:
            self.set_configuration( ix = entity_set_ix)
            # single entity_set results in configuration of (0,0)
            self.set_configuration( jx = entity_set_ix)
        elif entity_set_ix == 1:
            self.set_configuration( jx = entity_set_ix)
            
        return entity_set_ix


    def get_entities(self, entity_set_ix=0):
        """return the specified entity_set.

entity_set_ix is an integer that indexes into self.entity_sets"""
        # make sure the entity_set_index is valid
        self._validate_entity_set_index(entity_set_ix)
        return self.entity_sets[entity_set_ix].get_iterator()



    # @@ ISSUE: should the MolecularSystem maintain the coordinates
    # @@ as state. OR, should this actually change the values in whatever
    # @@ underlying Molecule representation that there is ??
    #
    # for now set_coords changes the MolKit values
    
    def set_coords(self, entity_set_ix, coords, coords_set_func=None):
        """provide new coords for the specified entitySet.
entity_set_ix is the index of an existing entitySet.
coords is a list (of proper length) of anything you want to use
to update coordinate with the coords_set_func you supply.
        """
        # validate input
        self._validate_entity_set_index(entity_set_ix)
        # assert <that coords is a list of coordinates>
        # check compatibility
        assert len(coords)==len(self.get_entities(entity_set_ix))

        if coords_set_func:
            for ex, e in enumerate(self.get_entities(entity_set_ix)):
                coords_set_func(e, coords[ex])
        else:
            #NB: this is MolKit AtomSet specific
            self.get_entities(entity_set_ix).updateCoords(coords)

        # clear distance matrix
        self.clear_dist_mat(entity_set_ix)


    def get_coords(self, entity_set_ix=0):
        """return the coordinates of the specified entity_set.

        DEPRECATED: use get_entities().coords instead.
        entity_set_ix is an integer that indexes into self.entity_sets
        """
        # raise DeprecationWarning, "use get_entities().coords instead"
        # validate input
        self._validate_entity_set_index(entity_set_ix)
        
        # get the coordinates accessor function
        accessor = self.coords_access_func_list[entity_set_ix]
        if accessor:
            coords = [accessor(e) for e in self.get_entities(entity_set_ix)]
        else:
            #in case getattr hasnot been overridden:
            coords = [e.coords for e in self.get_entities(entity_set_ix)] 
        return coords

# MolecularSystem

if __name__ == '__main__':
    print "unittests in Tests/test_MolecularSystem.py"
