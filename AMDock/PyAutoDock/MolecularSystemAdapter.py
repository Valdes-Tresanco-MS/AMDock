#
# $Id: MolecularSystemAdapter.py,v 1.5 2010/05/28 19:00:04 annao Exp $
#

"""
usage:
    adapter = Adapter[str(entity_set.__class__)](entity_set)
"""


class MolecularSystemAdapter:
    """abstract base class
    """
    def __init__(self):
        pass

    def get_iterator(self):
        pass
# MolecularSystemAdapter



class AtomSetAdapter(MolecularSystemAdapter):
    def __init__(self, atom_set):
        from MolKit.molecule import AtomSet
        assert( isinstance(atom_set, AtomSet))
        self.atom_set = atom_set
        MolecularSystemAdapter.__init__(self)

    def get_iterator(self):
        return self.atom_set

# AtomSetAdapter



class ResidueSetAdapter(MolecularSystemAdapter):
    def __init__(self, residue_set):
        from MolKit.protein import ResidueSet
        assert( isinstance(residue_set, ResidueSet))
        self.residue_set = residue_set
        MolecularSystemAdapter.__init__(self)

    def get_iterator(self):
        return self.residue_set

# ResidueSetAdapter



class GridMapAdapter(MolecularSystemAdapter):
    def __init__(self, grid_map):
        from AutoGrid import GridMap
        assert( isinstance(grid_map, GridMap))
        self.grid_map = grid_map
        MolecularSystemAdapter.__init__(self)

    def get_iterator(self):
        return self.grid_map.get_entity_list()

# GridMapAdapter

from MolKit.molecule import AtomSet
from MolKit.protein import ResidueSet

Adapters = {
    # class string : Adapter class
    str(AtomSet):AtomSetAdapter,
    'AutoDockSuite.AutoDockPy.AutoGrid.GridMap' : GridMapAdapter,
    'AutoDockPy.AutoGrid.GridMap' : GridMapAdapter,
    'PyAutoDock.AutoGrid.GridMap' : GridMapAdapter,
    str(ResidueSet) : ResidueSetAdapter,
    }

## Adapters = {
##     # class string : Adapter class
##     'MolKit.molecule.AtomSet': AtomSetAdapter,
##     'AutoDockSuite.AutoDockPy.AutoGrid.GridMap' : GridMapAdapter,
##     'AutoDockPy.AutoGrid.GridMap' : GridMapAdapter,
##     'PyAutoDock.AutoGrid.GridMap' : GridMapAdapter,
##     'MolKit.protein.ResidueSet' : ResidueSetAdapter,
##     }

