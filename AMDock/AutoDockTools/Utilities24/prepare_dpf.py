#!/usr/bin/env python
#
# 
#
# $Header: /opt/cvs/python/packages/share1.5/AutoDockTools/Utilities24/prepare_dpf.py,v 1.5 2011/11/30 18:02:01 rhuey Exp $
#

import string
import os.path
from MolKit import Read
from AutoDockTools.DockingParameters import DockingParameters, DockingParameterFileMaker, genetic_algorithm_list, \
                genetic_algorithm_local_search_list, local_search_list,\
                simulated_annealing_list



 

def usage():
    print "Usage: prepare_dpf.py -l pdbq_file -r pdbqs_file"
    print "    -l ligand_filename"
    print "    -r receptor_filename"
    print
    print "Optional parameters:"
    print "    [-o output dpf_filename]"
    print "    [-i template dpf_filename]"
    print "    [-p parameter_name=new_value]"
    print "    [-k list of parameters to write]"
    print "    [-L] use local search parameters"
    print "    [-S] use simulated annealing search parameters"
    print "    [-v] verbose output"
    print
    print "Prepare a docking parameter file (DPF) for AutoDock."
    print
    print "   The DPF will by default be <ligand>_<receptor>.dpf. This"
    print "may be overridden using the -o flag."

    
if __name__ == '__main__':
    import getopt
    import sys

    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'LShvl:r:i:o:p:k:')
    except getopt.GetoptError, msg:
        print 'prepare_dpf.py: %s' % msg
        usage()
        sys.exit(2)

    receptor_filename = ligand_filename = None
    dpf_filename = None
    template_filename = None
    parameters = []
    parameter_list = genetic_algorithm_local_search_list
    verbose = None
    for o, a in opt_list:
        if verbose: print "o=", o, ' a=', a
        if o in ('-v', '--v'):
            verbose = 1
            if verbose: print 'verbose output'
        if o in ('-l', '--l'):   #ligand filename
            ligand_filename = a
            if verbose: print 'ligand_filename =', ligand_filename
        if o in ('-r', '--r'):   #receptor filename
            receptor_filename = a
            if verbose: print 'receptor_filename =', receptor_filename
        if o in ('-i', '--i'):   #input reference
            template_filename = a
            if verbose: print 'template_filename =', template_filename
        if o in ('-o', '--o'):   #output filename
            dpf_filename = a
            if verbose: print 'output dpf_filename =', dpf_filename
        if o in ('-p', '--p'):   #parameter
            parameters.append(a)
            if verbose: print 'parameters =', parameters
        if o in ('-k', '--k'):   #parameter_list_to_write
            parameter_list = a
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-L', '--L'):   #parameter_list_to_write
            parameter_list = local_search_list
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-S', '--S'):   #parameter_list_to_write
            parameter_list = simulated_annealing_list
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-h', '--'):
            usage()
            sys.exit()


    if (not receptor_filename) or (not ligand_filename):
        print "prepare_dpf.py: ligand and receptor filenames"
        print "                    must be specified."
        usage()
        sys.exit()

    dm = DockingParameterFileMaker(verbose=verbose)
    if template_filename is not None:  #setup values by reading dpf
        dm.dpo.read(template_filename)
    dm.set_ligand(ligand_filename)
    dm.set_receptor(receptor_filename)
    #dm.set_docking_parameters( ga_num_evals=1750000,ga_pop_size=150, ga_run=20, rmstol=2.0)
    for p in parameters:
        key,newvalue = string.split(p, '=')
        #detect string reps of lists: eg "[1.,1.,1.]"
        if newvalue[0]=='[':
            nv = []
            for item in newvalue[1:-1].split(','):
                nv.append(float(item))
            #print "nv=", nv
            newvalue = nv
        kw = {key:newvalue}
        apply(dm.set_docking_parameters, (), kw)
    dm.write_dpf(dpf_filename, parameter_list)
    
#prepare_dpf.py -l indinavir.pdbq -r 1hsg.pdbqs -p ga_num_evals=20000000 -p ga_pop_size=150 -p ga_run=17 -i ref.dpf -o testing.dpf 

