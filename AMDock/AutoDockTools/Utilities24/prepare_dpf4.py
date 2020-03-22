#!/usr/bin/env python
#
# 
#
# $Header: /opt/cvs/python/packages/share1.5/AutoDockTools/Utilities24/prepare_dpf4.py,v 1.16 2011/11/30 18:02:01 rhuey Exp $
#

import string
import os.path
from MolKit import Read
from AutoDockTools.DockingParameters import DockingParameters, DockingParameter4FileMaker, genetic_algorithm_list, \
                genetic_algorithm_local_search_list4, local_search_list4,\
                simulated_annealing_list4
                


 

def usage():
    print "Usage: prepare_dpf4.py -l pdbqt_file -r pdbqt_file"
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
    print "Prepare a docking parameter file (DPF) for AutoDock4."
    print
    print "   The DPF will by default be <ligand>_<receptor>.dpf. This"
    print "may be overridden using the -o flag."

    
if __name__ == '__main__':
    import getopt
    import sys

    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'sLShvl:r:i:o:x:p:k:e')
    except getopt.GetoptError, msg:
        print 'prepare_dpf4.py: %s' % msg
        usage()
        sys.exit(2)

    receptor_filename = ligand_filename = None
    dpf_filename = None
    template_filename = None
    flexres_filename = None
    parameters = []
    parameter_list = genetic_algorithm_local_search_list4
    pop_seed = False
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
            #print 'parameters =', parameters
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
            parameter_list = local_search_list4
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-S', '--S'):   #parameter_list_to_write
            parameter_list = simulated_annealing_list4
            if verbose: print 'parameter_list =', parameter_list
        if o in ('-h', '--'):
            usage()
            sys.exit()
        if o in ('-s'):
            pop_seed = True


    if (not receptor_filename) or (not ligand_filename):
        print "prepare_dpf4.py: ligand and receptor filenames"
        print "                    must be specified."
        usage()
        sys.exit()


    #9/2011: fixing local_search bugs:
    # specifically: 
    # 1. quaternion0 0 0 0 0  
    # 2. dihe0 0 0 0 0 0 <one per rotatable bond>
    # 3. about == tran0 
    # 4. remove tstep  qstep and dstep
    # 5. remove ls_search_freq
    local_search = parameter_list==local_search_list4
    dm = DockingParameter4FileMaker(verbose=verbose)
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
        if newvalue[0]=='[':
            nv = []
            for item in newvalue[1:-1].split(','):
                nv.append(float(item))
            #print "nv=", nv
            newvalue = nv
        if key=='epdb_flag':
            print "setting epdb_flag to", newvalue
            kw['epdb_flag'] = 1
        elif key=='set_psw1':
            print "setting psw1_flag to", newvalue
            kw['set_psw1'] = 1
            kw['set_sw1'] = 0
        elif key=='set_sw1':
            print "setting set_sw1 to", newvalue
            kw['set_sw1'] = 1
            kw['set_psw1'] = 0
        elif key=='include_1_4_interactions_flag':
            kw['include_1_4_interactions'] = 1
        elif 'flag' in key:
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
        apply(dm.set_docking_parameters, (), kw)
        if key not in parameter_list:
            #special hack for output_pop_file
            if key=='output_pop_file':
                parameter_list.insert(parameter_list.index('set_ga'), key)
            else:
                parameter_list.append(key) 
    dm.write_dpf(dpf_filename, parameter_list, pop_seed)
    
#prepare_dpf4.py -l indinavir.pdbq -r 1hsg.pdbqs -p ga_num_evals=20000000 -p ga_pop_size=150 -p ga_run=17 -i ref.dpf -o testing.dpf 

