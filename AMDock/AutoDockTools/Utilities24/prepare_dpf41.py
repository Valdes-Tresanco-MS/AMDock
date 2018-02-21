#!/usr/bin/env python
#
# 
#
# $Header: /opt/cvs/python/packages/share1.5/AutoDockTools/Utilities24/prepare_dpf41.py,v 1.9 2011/12/01 17:52:54 rhuey Exp $
#

import string
import os.path
from MolKit import Read
from AutoDockTools.DockingParameters import DockingParameters, genetic_algorithm_list4_1, \
                genetic_algorithm_local_search_list4_1, local_search_list4_1,\
                simulated_annealing_list4_1, epdb_list4_2,\
                DockingParameter42FileMaker

from AutoDockTools.atomTypeTools import AutoDock4_AtomTyper
                

def usage():
    print "Usage: prepare_dpf41.py -l pdbqt_file -r pdbqt_file"
    print "    -l ligand_filename"
    print "    -r receptor_filename"
    print
    print "Optional parameters:"
    print "    [-o output dpf_filename]"
    print "    [-i template dpf_filename]"
    print "    [-x flexres_filename]"
    print "    [-p parameter_name=new_value]"
    print "    [-k list of parameters to write]"
    print "    [-e write epdb dpf ]"
    print "    [-v] verbose output"
    print "    [-L] use local search parameters"
    print "    [-S] use simulated annealing search parameters"
    print "    [-s] seed population using ligand's present conformation"
    print
    print "Prepare a docking parameter file (DPF) for AutoDock41."
    print
    print "   The DPF will by default be <ligand>_<receptor>.dpf. This"
    print "may be overridden using the -o flag."

    
if __name__ == '__main__':
    import getopt
    import sys

    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'sLShvl:r:i:o:x:p:k:e')
    except getopt.GetoptError, msg:
        print 'prepare_dpf41.py: %s' % msg
        usage()
        sys.exit(2)

    receptor_filename = ligand_filename = None
    dpf_filename = None
    template_filename = None
    flexres_filename = None
    parameters = []
    parameter_list = genetic_algorithm_local_search_list4_1
    pop_seed = False
    local_search = False
    verbose = None
    epdb_output = False
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
        if o in ('-x', '--x'):   #flexres_filename 
            flexres_filename = a
            if verbose: print 'flexres_filename =', flexres_filename
        if o in ('-i', '--i'):   #input reference
            template_filename = a
            if verbose: print 'template_filename =', template_filename
        if o in ('-o', '--o'):   #output filename
            dpf_filename = a
            if verbose: print 'output dpf_filename =', dpf_filename
        if o in ('-p', '--p'):   #parameter
            parameters.append(a)
            if verbose: print 'parameters =', parameters
        if o in ('-e', '--e'):
            epdb_output = True
            if verbose: print 'output epdb file'
            parameter_list = epdb_list4_2
        if o in ('-k', '--k'):   #parameter_list_to_write
            parameter_list = a
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-L', '--L'):   #parameter_list_to_write
            local_search = 1
            parameter_list = local_search_list4_1
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-S', '--S'):   #parameter_list_to_write
            parameter_list = simulated_annealing_list4_1
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-h', '--'):
            usage()
            sys.exit()
        if o in ('-s'):
            pop_seed = True


    if (not receptor_filename) or (not ligand_filename):
        print "prepare_dpf41.py: ligand and receptor filenames"
        print "                    must be specified."
        usage()
        sys.exit()


    dm = DockingParameter42FileMaker(autodock_parameter_version=4.1, verbose=verbose)
    if template_filename is not None:  #setup values by reading dpf
        dm.dpo.read(template_filename)
    dm.set_ligand(ligand_filename)
    dm.set_receptor(receptor_filename)
    if flexres_filename is not None:
        flexmol = Read(flexres_filename)[0]
        flexres_types = flexmol.allAtoms.autodock_element
        lig_types = dm.dpo['ligand_types']['value'].split()
        all_types = lig_types
        for t in flexres_types:
            if t not in all_types: 
                all_types.append(t)
        all_types_string = all_types[0]
        if len(all_types)>1:
            for t in all_types[1:]:
                all_types_string = all_types_string + " " + t
                if verbose: print "adding ", t, " to all_types->", all_types_string
        dm.dpo['ligand_types']['value'] = all_types_string 
        dm.dpo['flexres']['value'] = flexres_filename
        dm.dpo['flexres_flag']['value'] = True
    #dm.set_docking_parameters( ga_num_evals=1750000,ga_pop_size=150, ga_run=20, rmstol=2.0)
    kw = {}
    for p in parameters:
        key,newvalue = string.split(p, '=')
        #detect string reps of lists: eg "[1.,1.,1.]"
        if key=='parameter_file':
            if key in parameter_list:
                print "removing parameter_file keyword"
                parameter_list.remove('parameter_file')
            parameter_list.insert(1, key)
            dm.dpo['custom_parameter_file']['value']=1
        if newvalue[0]=='[':
            nv = []
            for item in newvalue[1:-1].split(','):
                nv.append(float(item))
            #print "nv=", nv
            newvalue = nv
            if verbose: print "newvalue=", nv
            kw[key] = nv
            if verbose: print "kw=", kw
        elif key=='epdb_flag':
            if verbose: print "setting epdb_flag to", newvalue
            kw['epdb_flag'] = 1
        elif 'flag' in key:
            if verbose: print "key=", key, ' newvalue=', newvalue
            if newvalue in ['1','0']:
                newvalue = int(newvalue)
            if newvalue =='False':
                newvalue = False
            if newvalue =='True':
                newvalue = True
        elif local_search and 'about' in key:
            kw['about'] = newvalue
            kw['tran0'] = newvalue     
        else:         
            kw[key] = newvalue
            print "set ", key, " to ", newvalue
        if verbose: print "calling set_docking_parameters with kw=", kw
        apply(dm.set_docking_parameters, (), kw)
        if key not in parameter_list:
            #special hack for output_pop_file
            if key=='output_pop_file':
                parameter_list.insert(parameter_list.index('set_ga'), key)
            else:
                parameter_list.append(key) 
    if epdb_output:
        dm.dpo['epdb_flag']['value'] = 1
        dm.write_dpf(dpf_filename, parm_list=epdb_list4_2)
    else:
        if verbose: print "not epdb_output else"
    dm.write_dpf(dpf_filename, parameter_list, pop_seed)
    
#prepare_dpf41.py -l indinavir.pdbqt -r 1hsg.pdbqt -p ga_num_evals=25000000 -p ga_pop_size=150 -p ga_run=17 -i ref.dpf -o testing.dpf 

