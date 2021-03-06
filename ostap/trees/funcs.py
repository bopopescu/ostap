#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file ostap/trees/funcs.py
#  Module with helper base classes ...
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2011-06-07
# =============================================================================
"""Decoration of Tree/Chain objects for efficient use in python"""
# =============================================================================
__version__ = "$Revision$"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2011-06-07"
__all__     = (
    'FuncTree'          , ## helper base class for 'TTree-function'
    'FuncData'          , ## helper base class for 'RooAbsData-function'
    'PyTreeFunction'    , ## 'TTree-function' that uses python function/callable 
    "pyfun_tree"        , ## ditto, but as fnuction 
    'PyDataFunction'    , ## 'Data-function' that uses python function/callable
    "pyfun_data"        , ## ditto, but as fnuction 
    'FuncFormula'       , ## simple wrapper over TTreeFormula/Ostap::Formula  
    'FuncRooFormula'    , ## simple wrapper over RooFormulaVar  
    'FuncTH1'           , ## TH1-based Tree-function 
    'FuncTH2'           , ## TH2-based Tree-function 
    'FuncTH3'           , ## TH3-based Tree-function 
    ) 
# =============================================================================
import ROOT
from   ostap.core.core import Ostap, valid_pointer
# =============================================================================
# logging 
# =============================================================================
from ostap.logger.logger import getLogger 
if '__main__' ==  __name__ : logger = getLogger( 'ostap.trees.funcs' )
else                       : logger = getLogger( __name__             )
# =============================================================================
## @class FuncTree
#  Helper class to implement "TTree-function"
#  @see Ostap::Functions::PyFuncTree
class FuncTree(Ostap.Functions.PyFuncTree) :
    """Helper class to implement ``TTree-function'' in python 
    """
    def __init__ ( self , tree = None ) :
        ## initialize the base class
        if tree is None : tree = 0 
        Ostap.Functions.PyFuncTree.__init__ ( self , self , tree )
        
    @property
    def the_tree ( self ) :
        """``the_tree'' : the actual pointer to the ROOT.TTree"""
        return self.tree ()
    
    ## the main method, abstract one 
    def evaluate ( self ) :
        tree = self.the_tree 
        assert valid_pointer ( tree ) , 'Invalid TTree object'
        return -1

# =============================================================================
## @class FuncData
#  Helper class to implement "RooAbsData-function"
#  @see Ostap::Functions::PyFuncData
class FuncData(Ostap.Functions.PyFuncData) :
    """Helper class to implement ``TTree-function''
    """
    def __init__ ( self , data = None ) :
        ## initialize the base class 
        Ostap.Functions.PyFuncData.__init__ ( self , self , data  ) 
        
    @property
    def the_data ( self ) :
        """``the_data'' : the actual pointer to the ROOT.RooAbsData"""
        return self.data ()
    
    ## the main method 
    def evaluate ( self ) :
        data = self.the_data
        assert valid_pointer ( data ), 'Invalid RooAbsData object'
        return -1

# =============================================================================
## @class PyTreeFunction
#  The concrete implementation on of <code>PyFunTree</code>, <code>FuncTree</code>
#  that delegates the evaluation to provided function/callable object
#  @see ostap.trees.funcs.FunTree
#  @see Ostap.Functions.PyFuncTree
#  @see Ostap.IFuncTree 
class PyTreeFunction(FuncTree) :
    """The concrete implementation on of PyFunTree, FuncTree,
    that delegates the evaluation to provided function/callable object
    - see ostap.trees.funcs.FunTree
    - see Ostap.Functions.PyFuncTree
    - see Ostap.IFuncTree 
    """
    def __init__ ( self , the_function , tree = None ) :
        """Constructor from the function/callable and (optional) tree"""
        FuncTree.__init__ ( self , tree  )
        assert callable   ( the_function ), \
               'PyTreeFunction:Invalid callable %s/%s'  ( the_function , type ( the_function ) )
        self.__function = the_function
        
    @property
    def the_function ( self ) :
        """``the_function'' : the actual function/callable object"""
        return self.__function
    
    ## the only one method, delegate to the function  
    def evaluate  ( self ) :
        tree = self.the_tree
        return self.__function ( tree )
    
# =============================================================================
## @class PyDataFunction
#  The concrete implementation on of <code>PyFuncData</code>, <code>FuncData</code>
#  that delegates the evaluation to provided function/callable object
#  @see ostap.trees.funcs.FuncData
#  @see Ostap.Functions.PyFuncData
#  @see Ostap.IFuncData 
class PyDataFunction(FuncData) :
    """The concrete implementation on of PyFunData, FuncData,
    that delegates the evaluation to provided function/callable object
    - see ostap.trees.funcs.FuncData
    - see Ostap.Functions.PyFuncData
    - see Ostap.IFuncData 
    """
    def __init__ ( self , the_function , data = None ) :        
        FuncData.__init__ ( self , data  )
        assert callable   ( the_function ), \
               'PyDataFunction:Invalid callable %s/%s'  ( the_function , type ( the_function ) )
        self.__function = the_function
        
    @property
    def the_function ( self ) :
        """``the_function'' : the actual function/callable object"""
        return self.__function
    
    ## the only one method, delegate to the function  
    def evaluate  ( self ) :
        data = self.the_data
        return self.__function ( tree )

# =================================================================================
## create the Ostap.ITreeFunc obejct from python function/callable
#  @code
#  def ququ ( tree ) : return tree.pz/tree.pt
#  fun = pyfun_tree ( ququ ) 
#  @endcode
#  @see Ostap::IFuncTree
#  @see Ostap::Functions::PyFuncTree 
#  @see ostap.funcs.FuncTree 
#  @see ostap.funcs.PyTreeFuction
def pyfun_tree ( function , tree = None ) :
    """Create the Ostap.ITreeFunc obejct from python function/callable
    >>> def ququ ( tree ) : return tree.pz/tree.pt
    >>> fun = pyfun_tree ( ququ )
    - see Ostap::IFuncTree
    - see Ostap::Functions::PyFuncTree 
    - see ostap.trees.funcs.FuncTree 
    - see ostap.trees.funcs.PyTreeFuction    
    """
    return PyTreeFunction ( function , tree ) 
    
# =================================================================================
## create the Ostap.IDataFunc obejct from python function/callable
#  @code
#  def ququ ( data ) : return data.pz/data.pt
#  fun = pyfun_data ( ququ ) 
#  @endcode
#  @see Ostap::IFuncData
#  @see Ostap::Functions::PyFuncData
#  @see ostap.funcs.FuncData 
#  @see ostap.funcs.PyDataFuction
def pyfun_data ( function , data = None ) :
    """Create the Ostap.IDataFunc obejct from python function/callable
    >>> def ququ ( data ) : return data.pz/data.pt
    >>> fun = pyfun_data ( ququ )
    - see Ostap::IFuncData
    - see Ostap::Functions::PyFuncData 
    - see ostap.trees.funcs.FuncData
    - see ostap.trees.funcs.PyDataFuction    
    """
    return PyDataFunction ( function , tree ) 
    

# =================================================================================
## the ITreeFunc based on TTree formula expression 
FuncFormula    = Ostap.Functions.FuncFormula

## the IDataFunc based on RooFormula machinery 
FuncRooFormula = Ostap.Functions.FuncRooFormula

FuncTH1        = Ostap.Functions.FuncTH1
FuncTH2        = Ostap.Functions.FuncTH2
FuncTH3        = Ostap.Functions.FuncTH3
         
# =============================================================================
if '__main__' == __name__ :
    
    from ostap.utils.docme import docme
    docme ( __name__ , logger = logger )
    
# =============================================================================
# The END 
# =============================================================================
