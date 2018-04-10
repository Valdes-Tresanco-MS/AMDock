from pymol.preset import *
from pymol import cmd
import sys, getopt, re, os

opt_list, args = getopt.getopt(sys.argv[1:], 't:o:')

for o, a in opt_list:
    if o in ('-t', '--t'):
        target = a
    if o in ('-o','--o'):
        offtarget = a

cmd.load(target, 'target')
cmd.load(offtarget, 'offtarget')
cmd.align('offtarget', 'target')
os.remove(offtarget)
cmd.save(offtarget, 'offtarget')



