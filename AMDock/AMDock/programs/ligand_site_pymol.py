from pymol.preset import *
from pymol import cmd
from pymol.util import *
import sys

args = sys.argv[1:]
target = None
offtarget = None
# 1- representation, 2- protein, 3- prot_type (target or off-target), 4- poses
# rep = args[0]
if len(args):
    target = args[0].split(',')
if len(args) == 2:
    offtarget = args[1].split(',')

def representation(mode='cartoon'):
    cmd.bg_color('white')
    cmd.remove('hydro')
    if mode == 'cartoon':
        ligand_cartoon()
    elif mode == 'ribbon':
        ligands()
    elif  mode == 'surface':
        ligand_sites()

# def load_rep(rep, prot, prot_type, *args):
def load_rep(target, offtarget):
    tprot = target[0]
    tprot_type = target[1]
    tligs = target[2:]

    cmd.load(tprot, tprot_type)
    for lig in tligs:
        cmd.load(lig, '%s_poses' % tprot_type[0])
    ligand_cartoon('(%s_poses or %s)' % (tprot_type[0], tprot_type))
    cmd.set_name('polar_contacts', '%s_polar_contacts' % tprot_type[0])
    util.cbag('(%s_poses or %s)' % (tprot_type[0], tprot_type))
    if offtarget:
        oprot = offtarget[0]
        oprot_type = offtarget[1]
        oligs = offtarget[2:]

        cmd.load(oprot, 'Off-Target')
        for lig in oligs:
            cmd.load(lig, 'O_poses')
        ligand_cartoon('(O_poses or Off-Target)')
        cmd.set_name('polar_contacts', 'O_polar_contacts')
        util.cbam('(O_poses or Off-Target)')
    # cmd.bg_color('white')
    # representation(rep)
    cmd.remove("all & hydro & not nbr. (don.|acc.)")


load_rep(target, offtarget)

# representation()



