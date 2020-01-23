#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file ostap/parallel/tests/test_parallel_dill.py
#  Test for dill serializer
#  @see https://github.com/uqfoundation/dill
#  @author Vanya BELYAEV Ivan.Belyaeve@itep.ru
#  @date 2020-01-23
# =============================================================================
"""Test for dill serializer 
- https://github.com/uqfoundation/dill
"""
# =============================================================================
__version__ = "$Revision:"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2014-06-08"
__all__     = ()  ## nothing to be imported 
# =============================================================================
import ROOT, pickle, sys 
# =============================================================================
# logging 
# =============================================================================
from ostap.logger.logger import getLogger 
if '__main__' == __name__ or '__builtin__' == __name__ : 
    logger = getLogger( 'ostap.test_parallel_dill' )
else : 
    logger = getLogger( __name__ )
# =============================================================================
try :
    import dill
except ImportError :
    logger.error ( "dill module can not be imported!" )
    dill = None


# =============================================================================
def test_dill () :

    h = ROOT.TH1D()
    
    logger.info ( "Python version: %s.%s.%s" % ( sys.version_info.major ,
                                                 sys.version_info.minor ,
                                                 sys.version_info.micro ) )
    logger.info ( "ROOT   version: %s"       % ROOT.gROOT.GetVersion()  )
    
    if dill and dill.__version__ : 
        logger.info ( "dill   version: %s"       % dill.__version__      )
        
    try : 
        p = pickle.dumps  ( h )
        logger.info  ("Histogram is successfully serialized using pickle!")
    except PickleError :
        logger.error ("Histogram cannot be serialized using pickle!")
        
    try : 
        d = dill  .dumps  ( h ) 
        logger.info  ("Histogram is successfully serialized using dill!")
    except PickleError :
        logger.error ("Histogram cannot be serialized using dill!")


# =============================================================================
if '__main__' == __name__ :

    if dill : test_dill ()
    
# =============================================================================
##                                                                      The END 
# =============================================================================
