from pymol.preset import *
from pymol import cmd

def representation():
    cmd.remove('hydro')
    pretty('(all)')

representation()



