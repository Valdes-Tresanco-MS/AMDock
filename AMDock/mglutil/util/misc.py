## Automatically adapted for numpy.oldnumeric Jul 23, 2007 by 

#############################################################################
#
# Author: Michel F. SANNER
#
# Copyright: M. Sanner TSRI 2000
#
#############################################################################

#
# $Header: /opt/cvs/python/packages/share1.5/mglutil/util/misc.py,v 1.19 2011/08/18 18:26:53 sanner Exp $
#
# $Id: misc.py,v 1.19 2011/08/18 18:26:53 sanner Exp $
#

import types
import sys
import numpy.oldnumeric as Numeric
import os

_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey):
    '''Private.
    '''
    global _proc_status, _scale
     # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
     # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
     # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


def issequence(a):
    return type(a) is types.TupleType or \
           type(a) is types.ListType or \
           isinstance(a, Numeric.ArrayType)

def isnumericstring(a):
    try:
        float(a)
        return 1
    except:
        return 0

def uniq(objectSequence):
    """Remove the duplicates from a list while keeping the original
    list order """
    l = []
    d = {}
    for o in objectSequence:
        if not d.has_key(o):
            d[o] = None
            l.append(o)
    return l


def deepCopySeq(sequence):
    """ returns the deep copy of the given sequence """
    import numpy.oldnumeric as Numeric
    from types import TupleType, ListType
    assert type(sequence) in (TupleType, ListType, type(Numeric.array([1,2,3])))
    if hasattr(sequence, 'copy'):
        dcSeq = sequence.copy()
    else:
        dcSeq = sequence[:]

    return dcSeq


def ensureFontCase(font):
    return font
#    from Tkinter import TkVersion
#    lFont = font[0].upper() + font[1:].lower()
#    if TkVersion == '8.4' and sys.platform != "win32":
#        lFont = font.lower()
#    return lFont


def isInstance(lObject):

    import types
    if sys.version.startswith('2.5'): #detect python25
        if type(lObject) == types.InstanceType:
            return True
        else:
            return False
    else:
            import inspect
            ltype = type(lObject)
            if ltype == types.InstanceType:
                return True
            elif inspect.isclass(lObject) is False \
              and isinstance(lObject, ltype) is True:
                from abc import ABCMeta
                if ltype == types.ClassType is True:
                    return True
                elif type(ltype) == ABCMeta:
                    return True
                else:
                    return False
            else:
                return False


def importMainOrIPythonMain():
    try:
        from IPython import ipapi
        mainDict = ipapi.get().user_ns
    except:
        mainDict = __import__('__main__').__dict__
    return mainDict


def suppressMultipleQuotes(aString):
    lStringToSimplify = aString
    lSimplifiedString = lStringToSimplify
    while type(lStringToSimplify) == types.StringType:
        lSimplifiedString = lStringToSimplify
        try:
           lStringToSimplify = eval(lSimplifiedString)
        except:
           break
    return lSimplifiedString


class IntVar:
    def __init__(self, val=0):
        self.set(val)

    def get(self):
        return self.val

    def set(self,val):
        self.val = int(val)


class StringVar:
    def __init__(self, val=""):
        self.set(val)

    def get(self):
        return self.val

    def set(self,val):
        self.val = str(val)


class BooleanVar:
    def __init__(self, val=False):
        self.set(val)

    def get(self):
        return self.val

    def set(self,val):
        self.val = (val==True)
