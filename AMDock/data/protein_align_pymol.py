from pymol.preset import *
from pymol import cmd
import sys, getopt, re, os

opt_list, args = getopt.getopt(sys.argv[1:], 't:o:')

for o, a in opt_list:
    if o in ('-t', '--t'):
        target = a
    if o in ('-o','--o'):
        offtarget = a
try:
    cmd.load(target, 'target')
    cmd.load(offtarget, 'offtarget')
    data = cmd.align('offtarget', 'target')
    os.remove(offtarget)
    cmd.save(offtarget, 'offtarget')
    # data from pymol wiki after align
    print("ALIGN > %10.02f RMSD after refinement" % data[0]) # RMSD after refinement
    print("ALIGN > %10d Number of aligned atoms after refinement" % data[1]) # Number of aligned atoms after refinement
    print("ALIGN > %10d Number of refinement cycles" % data[2]) # Number of refinement cycles
    print("ALIGN > %10.02f RMSD before refinement" % data[3]) # RMSD before refinement
    print("ALIGN > %10d Number of aligned atoms before refinement" % data[4]) # Number of aligned atoms before refinement
    print("ALIGN > %10.01f Raw alignment score" % data[5]) # Raw alignment score
    print("ALIGN > %10d Number of residues aligned" % data[6]) # Number of residues aligned
except:
    sys.exit(1)