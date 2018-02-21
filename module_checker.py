#!/usr/bin/python

import os, shutil, subprocess
installerdir = os.path.split(__file__)[0]
try:
    import numpy
    numpyloc = os.path.split(numpy.__file__)[0]
except ImportError:
    raise ImportError('You must be install numpy!!!!')

#check if exist oldnumeric in numpy module
try:
    import numpy.oldnumeric
except:
    shutil.copytree(os.path.join(installerdir,'oldnumeric'), numpyloc)
#check if exist openbabel
try:
    obabel_exe = subprocess.Popen(['obabel','-V'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)
except EnvironmentError:
    raise EnvironmentError('You must be install Openbabel. You can type in your terminal sudo apt-get install openbabel')
else:
    #check if version is > 2.3.0
    obmayor, obminor, obrel = obabel_exe.communicate()[0].split()[2].split('.')
    if obmayor < 2:
        raise StandardError('Openbabel version must be > 2.3.0')
    elif obminor < 3:
        raise StandardError('Openbabel version must be > 2.3.0')
# check if exist pymol
try:
    pymol_exe = subprocess.Popen(['pymol', '-c'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)
except EnvironmentError:
    raise EnvironmentError('You must be install Pymol. You can type in your terminal sudo apt-get install pymol')

try:
    import PyQt4
except:
    raise ImportError('You must be install PyQt4. You can type in your terminal sudo apt-get install python-qt4')
