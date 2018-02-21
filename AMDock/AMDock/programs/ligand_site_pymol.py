from pymol.preset import *
from pymol import cmd

def representation(mode='cartoon'):
    cmd.bg_color('white')
    cmd.remove('hydro')
    if mode == 'cartoon':
        ligand_cartoon()
    elif mode == 'ribbon': 
        ligands()
    elif  mode == 'surface':
        ligand_sites()

representation()



