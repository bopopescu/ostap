#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file
#  Module with some simple but useful utilities
#   - suppression of stdout/stderr 
#   - dumpting of stdout/stderr into file 
#
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2013-02-10
#  
# =============================================================================
"""Module with some simple but useful utilities"""
# =============================================================================
__version__ = "$Revision$"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2013-02-10"
# =============================================================================
__all__     = (
    #
    'tee_py'             , ## tee for Python's printouts
    'tee_cpp'            , ## tee for C++'s    printouts
    'output'             , ## redirect stdout/stderr into the file 
    'mute_py'            , ## suppress stdout/strerr Python printout 
    'silence_py'         , ## ditto 
    'mute'               , ## context manager to suppress stdout/strerr printout 
    'silence'            , ## ditto 
    'rooSilent'          , ## control RooFit verbosity
    'roo_silent'         , ## control RooFit verbosity 
    'rootError'          , ## control ROOT verbosity 
    'rootWarning'        , ## control ROOT verbosity 
    'NoContext'          , ## empty context manager
    'RooSilent'          , ## control RooFit verbosity
    'ROOTIgnore'         , ## control ROOT verbosity, suppress ROOT errors
    ## logging   
    'logColor'           , ## switch on   locally the colored logging
    'logNoColor'         , ## switch off locally the colored logging
    'logVerbose'         , ## redefine (locally) the logging level
    'logDebug'           , ## redefine (locally) the logging level
    'logInfo'            , ## redefine (locally) the logging level
    'logWarning'         , ## redefine (locally) the logging level
    'logError'           , ## redefine (locally) the logging level
    ## convert ROOT Errors into C++/python exceptions 
    'rootException'      , ## context manager to perform ROOT Error -> C++/Python exception
    'RootError2Exception', ## context manager to perform ROOT Error -> C++/Python exception
    ##
    'pretty_float'       , ## printpouit of the floatig number 
    'pretty_ve'          , ## printpouit of the value with error 
    'pretty_2ve'         , ## printpouit of the value with asymmetric errors 
    ##
    'multicolumn'        , ## format the list of strings into multicolumn block
    'DisplayTree'        , ## display tree-like structures 
    )
# =============================================================================
import ROOT,cppyy, time, os,sys ## attention here!!
cpp = cppyy.gbl
ROOT_RooFit_ERROR = 4 
# =============================================================================
# logging 
# =============================================================================
from   ostap.logger.logger    import getLogger, logColor, logNoColor 
if '__main__' ==  __name__ : logger = getLogger( 'ostap.logger.utils' )
else                       : logger = getLogger( __name__ )
del getLogger 
from   ostap.logger.logger    import logVerbose,  logDebug, logInfo, logWarning, logError
from   ostap.utils.utils      import RootError2Exception, rootException
from   ostap.core.ostap_types import integer_types, num_types  
# =============================================================================
## @class MutePy
#  Very simple context manager to suppress python printout 
class MutePy(object):
    """A context manager for doing a ``deep suppression'' of stdout and stderr in 
    Python, i.e. will suppress all print, even if the print originates in a 
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).      
    
    stallen from  
    http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
    """
    def __init__( self , out = True , err = False ):
        self._out = out
        self._err = err
        
    def __enter__(self):
        #
        ## helper class to define empty stream 
        class Silent(object):
            def write(self,*args,**kwards) : pass

        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
        if self._out : sys.stdout = Silent() 
        if self._err : sys.stderr = Silent() 

        return self
    
    def __exit__(self, *_):
        
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        
# ============================================================================
## @class MuteC
#  context manager to suppress pythion prinout
#  the actual code is stallen from
#  http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
#  A fix is added for "IOError: [Errno 24] Too many open files" :
#  original code leaks the file descriptors
class MuteC(object):
    """A context manager for doing a ``deep suppression'' of stdout and stderr in 
    Python, i.e. will suppress all print, even if the print originates in a 
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).      
    
    stallen from  
    http://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
    """
    #
    ## class variables: dev-null device & instance counter 
    _devnull = 0
    _cnt     = 0
    
    def __init__( self , out = True , err = False ):
        
        self._out = out
        self._err = err

        # increment instance counter 
        self.__class__._cnt += 1

        # create dev-null if not done yet 
        if not self.__class__._devnull :
            self.__class__._devnull = os.open ( os.devnull , os.O_WRONLY )            

    def __del__  ( self ) :
        
        # decrement instance counter 
        self.__class__._cnt -= 1
        
        # close dev-null if not done yet 
        if self.__class__._cnt <= 0 and self.__class__._devnull : 
            os.close ( self.__class__._devnull  )
            self.__class__._devnull = 0
            

    ## context-manager 
    def __enter__(self):
        
        ## Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds =  os.dup(1), os.dup(2)  # leak was here !!!
        
        ## mute it!
        if self._out : os.dup2 ( self.__class__._devnull , 1 )  ## C/C++
        if self._err : os.dup2 ( self.__class__._devnull , 2 )  ## C/C++

        return self
    
    ## context-manager 
    def __exit__(self, *_):
        
        # Re-assign the real stdout/stderr back to (1) and (2)  (C/C++)
        if self._err : os.dup2 ( self.save_fds[1] , 2 )
        if self._out : os.dup2 ( self.save_fds[0] , 1 )
        
        # fix the  file descriptor leak
        # (there were no such line in example, and it causes
        #      the sad:  "IOError: [Errno 24] Too many open files"
        
        os.close ( self.save_fds[1] ) 
        os.close ( self.save_fds[0] )
                
# =============================================================================
## dump all stdout/stderr information (including C/C++) into separate file
#  @code
#  with output ('output.txt') :
#           print 'ququ!'
#  @endcode 
#  @see MuteC 
class OutputC(object) :
    """Dump all stdout/stderr information into separate file:    
    >>>  with output ('output.txt') :
    ...             print 'ququ!'    
    """
    ## constructor: file name 
    def __init__ ( self , filename , out = True , err = False ) : 
        """Constructor
        """
        self._out  = out 
        self._err  = err
        self._file = open ( filename , 'w' ) 
            
    ## context-manager 
    def __enter__(self):
        
        if self._out : sys.stdout.flush()
        if self._err : sys.stderr.flush()
        
        self._file.flush()
        
        self._file.__enter__ () 
        ## Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds =  os.dup(1), os.dup(2)  # leak was here !!!
        
        ## mute it!
        if self._out : os.dup2 ( self._file.fileno() , 1 )  ## C/C++
        if self._err : os.dup2 ( self._file.fileno() , 2 )  ## C/C++

        return self
    
    ## context-manager 
    def __exit__( self , *_ ):

        if self._out : sys.stdout.flush()
        if self._err : sys.stderr.flush()
        
        self._file.flush()
        
        # Re-assign the real stdout/stderr back to (1) and (2)  (C/C++)
        if self._err : os.dup2 ( self.save_fds[1] , 2 )
        if self._out : os.dup2 ( self.save_fds[0] , 1 )
        
        # fix the  file descriptor leak
        # (there were no such line in example, and it causes
        #      the sad:  "IOError: [Errno 24] Too many open files"        
        os.close ( self.save_fds[1] ) 
        os.close ( self.save_fds[0] )
        
        self._file.__exit__ ( *_ )
        
        sys.stdout.flush()
        sys.stderr.flush()
        

# =============================================================================
## very simple context manager to duplicate Python-printout into file ("tee")
#  into separate file
#  @code
#  with tee('tee.txt') :
#           print 'ququ!'
#  @endcode
#  @attention: only Python printouts are grabbed 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2012-07-06
class TeePy(object) :
    """Very simple context manager to duplicate Python-printout into file (``tee'')
    into separate file
    
    >>>  with tee('tee.txt') :
    ...        print 'ququ!'
    
    Unfortunately only Python printouts are grabbed 
    """
    ## constructor 
    def __init__( self , filename ):
        
        self._file = open ( filename , 'w' ) 

    ## context manager 
    def __enter__(self):
        
        self._file . __enter__ ()
        
        ## helper class to define empty stream 
        class _Tee(object):
            def __init__ ( self , the_file , the_stream ) :
                
                self._stream = the_stream 
                self._log    = the_file
                
            def write(self,*args) :
                
                self._stream .write ( *args ) 
                self._log    .write ( *args )
                
        self.stdout =  sys.stdout        
        sys.stdout  = _Tee ( self._file , self.stdout ) 

        return self
    
    ## context manager 
    def __exit__(self, *_):

        self._file.flush  ()
        self.stdout.flush ()
        
        sys.stdout = self.stdout
        
        self._file.__exit__ ( *_ )

# =============================================================================
## very simple context manager to duplicate C++-printout into file ("tee")
#  into separate file
#  @code
#  >>> with tee_cpp('tee.txt') :
#  ...         some_cpp_function() 
#  @endcode
#  @see Ostap::Utils::Tee
#  @attention: Python&C-printouts probably  are not affected 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2012-07-07
class TeeCpp(object) :
    """Very simple context manager to duplicate C++-printout into file 
    into separate file
    
    >>> with tee_cpp('tee.txt') :
    ...         some_cpp_function()
    
    """
    def __init__ ( self , fname ) :
        sys.stdout.flush ()
        sys.stderr.flush ()
        self.__tee = cpp.Ostap.Utils.Tee ( fname ) 
        
    ## context manager
    def __enter__ ( self      ) :
        sys.stdout.flush ()
        sys.stderr.flush ()
        self.__tee.enter ()
        return self
    
    ## context manager
    def __exit__  ( self , *_ ) :
        self.__tee.exit  ()
        del self.__tee
        sys.stdout.flush ()
        sys.stderr.flush ()
        
# =============================================================================
## very simple context manager to suppress RooFit printout
#
#  @code
#
#  >>> with rooSilent( 4 , False ) :
#  ...        some_RooFit_code_here()
#
#  @endcode
#  @see RooMgsService
#  @see RooMgsService::globalKillBelow
#  @see RooMgsService::silentMode 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2013-07-09
class RooSilent(object) :
    """Very simple context manager to suppress RooFit printout
    
    >>> with rooSilent( 4 , False ) :
    ...        some_RooFit_code_here ()
    
    """
    ## constructor
    #  @param level  (INPUT) print level 
    #  @param silent (print level 
    # 
    def __init__ ( self , level = ROOT_RooFit_ERROR , silent = True ) :
        """ Constructor
        @param level  (INPUT) print level 
        @param silent (print level 
        
        >>> with rooSilent( ROOT.RooFit.ERROR , True  ) :
        ...        some_RooFit_code_here ()
        
        
        >>> with rooSilent( ROOT.RooFit.INFO , False  ) :
        ...        some_RooFit_code_here ()
        
        
        """
        #
        if level > ROOT.RooFit.FATAL : level = ROOT.RooFit.FATAL 
        if level < ROOT.RooFit.DEBUG : level = ROOT.RooFit.DEBUG 
        #
        self._level  = level 
        self._silent = True if silent else False  
        self._svc    = ROOT.RooMsgService.instance()
        
    ## context manager
    def __enter__ ( self ) :

        self._prev_level  = self._svc.globalKillBelow  () 
        self._prev_silent = self._svc.silentMode       () 
        
        self._svc.setGlobalKillBelow  ( self._level      )
        self._svc.setSilentMode       ( self._silent     )
        
        return self
    
    ## context manager 
    def __exit__ ( self , *_ ) : 
            
        self._svc.setSilentMode      ( self._prev_silent )
        self._svc.setGlobalKillBelow ( self._prev_level  )


# =============================================================================
## Very simple context manager to suppress ROOT printout
#  @code
#  >>> with ROOTIgnore( ROOT.kError + 1 ) : some_ROOT_code_here()
#  @endcode
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2015-07-30
class ROOTIgnore( object ) :
    """Very simple context manager to suppress ROOT printout
    >>> with ROOTIgnore ( ROOT.kError + 1 ) : some_ROOT_code_here()
    """
    ## constructor
    #  @param level  (INPUT) print level 
    #  @param silent (print level 
    # 
    def __init__ ( self , level ) :
        """ Constructor:        
        >>> with rootError   () : some_ROOT_code_here()
        >>> with rootWarning () : some_ROOT_code_here()
        """
        #
        self._level = int( level )
        
    ## context manager: ENTER 
    def __enter__ ( self ) :
        "The actual context manager: ENTER" 
        self._old = int ( ROOT.gErrorIgnoreLevel ) 
        if self._old != self._level : 
            ROOT.gROOT.ProcessLine("gErrorIgnoreLevel= %d ; " % self._level ) 
            
        return self
    
    ## context manager: EXIT 
    def __exit__ ( self , *_ ) : 
        "The actual context manager: EXIT"             
        if self._old != int ( ROOT.gErrorIgnoreLevel )  : 
            ROOT.gROOT.ProcessLine("gErrorIgnoreLevel= %d ; " % self._old ) 
            
# =============================================================================
## @class NoContext
#  Fake empty context manager to be used as empty placeholder
#  @code
#  with NoContext() :
#  ...  do_something() 
#  @endcode 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2013-01-12
class NoContext(object) :
    """ Fake (empty) context manager to be used as empty placeholder
    >>> with NoContext() :
    ...         do_something() 
    """
    def __init__  ( self , *args , **kwargs ) : pass
    ## context manager
    def __enter__ ( self         ) : return self 
    ## context manager 
    def __exit__  ( self , *args ) : pass  


# =============================================================================
## very simple context manager to duplicate Python-printout into file ("tee")
#  into separate file
#  @code
#  >>> with tee_py ('tee.txt') :
#  ...         print 'ququ!'
#  @endcode
#  @attention: only Python prinouts are grabbed 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2012-07-06
def tee_py ( filename ) :
    """Very simple context manager to duplicate Python-printout into file ("tee")
    into separate file
    >>> with tee('tee.txt') :
    ...        print 'ququ!'
    Unfortunately only Python printouts are grabbed 
    """
    return TeePy ( filename ) 
    
# =============================================================================
## very simple context manager to duplicate C++-printout into file ('tee')
#  into separate file
#  @code
#  >>> with tee_cpp ('tee.txt') : some_cpp_code() 
#  @endcode
#  @attention: only C/C++ printouts are grabbed 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2012-07-06
def tee_cpp ( filename ) :
    """Very simple context manager to duplicate C++-printout into file ('tee')
    into separate file
    >>> with tee_cpp('tee.txt') : some_cpp_code()
    Unfortunately only C/C++ printouts are grabbed 
    """
    return TeeCpp ( filename ) 


# =============================================================================
## simple context manager to redirect all (C/C++/Python) printout 
#  into separate file
#  @code
#  >>> with output ('output.txt') :
#  ...         print 'ququ!'
#  @endcode 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  date 2012-07-06
def output ( fname , cout = True , cerr = False ) :
    """ Simple context manager to redirect all (C/C++/Python) printotu
    
    >>> with output ('output.txt') :
    ...               print 'ququ!'
    
    """
    return OutputC ( fname  , cout , cerr )

# =============================================================================
## simple context manager to suppress C/C++-printout
#
#  @code
#  >>> with mute () :
#  ...        <some code here>
#  @endcode 
def mute ( cout = True , cerr = False )   :
    """Simple context manager to suppress C/C++ printout
    
    >>> with mute () :
    ...     <some code here>
    """
    return MuteC ( cout , cerr )

# =============================================================================
## simple context manager to suppress Python-printout
#
#  @code
#  >>> with mute_py () :
#  ...        <some code here>
#  @endcode 
def mute_py ( cout = True , cerr = False )   :
    """Simple context manager to suppress python printouts
    
    >>> with mute_py () :
    ...    <some code here>    
    """
    return MutePy ( cout , cerr )

# ==============================================================================
## ditto 
silence_py  = mute_py  # ditto
silence     = mute     # ditto


# =============================================================================
## very simple context manager to suppress RooFit printout
#
#  @code
#
#  >>> with rooSilent( 4 , False ) :
#  ...        some_RooFit_code_here()
#
#  @endcode
#  @see RooMgsService
#  @see RooMgsService::globalKillBelow
#  @see RooMgsService::silentMode 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2013-07-09
def rooSilent ( level = ROOT_RooFit_ERROR , silent = True ) :
    """Very simple context manager to suppress RooFit printout
    >>> with rooSilent( 4 , False ) :
    ...        some_RooFit_code_here()    
    """
    return RooSilent ( level , silent ) 

# =============================================================================
## helper context manager
#  @code
#
#  >>> with roo_silent( True ) : 
#  ...        some_RooFit_code_here()
#
#  @endcode
#  @see rooSilent
#  @see NoContex
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2013-07-09
def roo_silent ( silence , *args ) :
    """ Helper context manager#
    >>> with roo_silent ( True ) : 
    ...        some_RooFit_code_here()
    """
    return rooSilent ( *args ) if silence else NoContext() 

# =============================================================================
## very simple context manager to suppress ROOT printout
#  @code
#  >>> with rootError () : some_ROOT_code_here()
#  @endcode
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2015-07-30
def rootError   ( level = 1 ) :
    """Very simple context manager to suppress ROOT printout
    >>> with rootError () : some_ROOT_code_here()
    """
    return ROOTIgnore ( ROOT.kError   + level )

# =============================================================================
## very simple context manager to suppress ROOT printout
#  @code
#  >>> with rootError () : some_ROOT_code_here()
#  @endcode
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date   2015-07-30
def rootWarning ( level = 1 ) :
    """Very simple context manager to suppress ROOT printout
    >>> with rootWarning () : some_ROOT_code_here()
    """
    return ROOTIgnore ( ROOT.kWarning + level )

# =============================================================================
## nice printout of the floating number (string + exponent)
#  @code
#  s , n = pretty_float ( number ) 
#  @endcode
#  @return nice stirng and the separate exponent 
def pretty_float ( value , width = 8 , precision = 6 ) :
    """N Nice printout of the floating number
    - return nice string and the separate exponent 
    >>> s , n = pretty_float ( number ) 
    """
    assert isinstance ( value     , num_types     ),\
           'Invalid value parameter %s/%s'   % ( value , type ( value ) )      
    assert isinstance ( width     , integer_types ) and \
           isinstance ( precision , integer_types ) and 2 <= precision < width, \
           "Invalid width/precision parameters %s/%s" % ( width , precision ) 

    
    v  = value 
    av = abs ( v ) 
    if   100 <= av < 1000 :
        fmt2 = '%%+%d.%df' % ( width , precision - 2 )
        return fmt2 % v , None
    elif 10  <= av < 100  :
        fmt1 = '%%+%d.%df' % ( width , precision - 1 )
        return fmt1 % v , None 
    elif 1   <= av < 10   :
        fmt0 = '%%+%d.%df' % ( width , precision     )
        return fmt0 % v , None 
    
    from  ostap.math.base        import frexp10 
    v_a , v_e = frexp10 ( av )
    
    v_a *= 10
    v_e -=  1 

    n , r = divmod  ( v_e , 3 )
    if 0 != r : 
        r -= 3
        n += 1
        
    ra = v_a * ( 10**r )

    fmt0 = '%%+%d.%df' % ( width , precision     )
    return fmt0 % ( ra ) , 3 * n

# ===============================================================================
## nice printout of the ValueWithError obejct  ( string + exponent)
#  @code
#  s , n = pretty_ve ( number ) 
#  @endcode
#  @return nice stirng and the separate exponent 
def pretty_ve ( value , width = 8 , precision = 6 ) :
    """Nice printout of the ValueWithError obejct  ( string + exponent)
    - return nice stirng and the separate exponent 
    >>> s , n = pretty_ve ( number ) 
    """
    
    from ostap.math.ve import VE
    
    v =           value.value ()
    e = max ( 0 , value.error () )

    assert isinstance ( value , VE ), 'Invalid type for value %s' % value 

    assert isinstance ( width     , integer_types ) and \
           isinstance ( precision , integer_types ) and 2 <= precision < width, \
           "Invalid width/precision parameters %s/%s" % ( width , precision ) 
    
    av = max ( abs ( v ) ,  e )

    if   100 <= av < 1000 :
        fmt2 = '( %%+%d.%df +/- %%-%d.%df )' % ( width , precision - 2 , width , precision - 2 )
        return fmt2 % ( v , e ) , None
    elif 10  <= av < 100  :
        fmt1 = '( %%+%d.%df +/- %%-%d.%df )' % ( width , precision - 1 , width , precision - 1 )   
        return fmt1 % ( v , e ) , None 
    elif 1   <= av < 10   :
        fmt0 = '( %%+%d.%df +/- %%-%d.%df )' % ( width , precision     , width , precision     )
        return fmt0 % ( v , e ) , None 

    from  ostap.math.base        import frexp10 
    v_a , v_e = frexp10 ( av )

    v /= 10**(v_e-1)
    e /= 10**(v_e-1)
    
    v_e -= 1     
    n , r = divmod  ( v_e , 3 )    
    if 0 != r : 
        r -= 3
        n += 1

    v *= 10**r
    e *= 10**r 

    fmt0 = '( %%+%d.%df +/- %%-%d.%df )' % ( width , precision     , width , precision     )
    return fmt0 % ( v  , e ) , 3 * n


# ===============================================================================
## nice printout of the object with asymmetric  errors   ( string + exponent)
#  @code
#  s , n = pretty_2ve ( number , ehigh , elow ) 
#  @endcode
#  @return nice string and the separate exponent 
def pretty_2ve ( value         ,
                 eh            ,
                 el            ,
                 width     = 8 ,
                 precision = 6 ) :
    
    assert isinstance ( value     , num_types     ),\
           'Invalid value parameter %s/%s'   % ( value , type ( value ) )      
    assert isinstance ( eh       , num_types     ),\
           'Invalid eh    parameter %s/%s'   % ( eh    , type ( eh    ) )      
    assert isinstance ( el       , num_types     ),\
           'Invalid el    parameter %s/%s'   % ( el    , type ( el    ) )      

    v = value 
    e = max ( abs ( eh ), abs ( el ) )

    assert isinstance ( width     , integer_types ) and \
           isinstance ( precision , integer_types ) and 2 <= precision < width, \
           "Invalid width/precision parameters %s/%s" % ( width , precision ) 

    assert 0 <= eh or 0 <= el, 'Both errors cannot be negative!'
    
    if   eh < 0  and el < 0 :
        eh , el =   el , eh
    elif eh >= 0 and el < 0 :
        eh , el = eh , abs ( el )
    
    av = max ( abs ( v ) ,  e )

    if   100 <= av < 1000 :
        fmt2  = '( %%+%d.%df +/%%-%d.%df -/%%-%d.%df )' %  ( width , precision - 2 , width , precision - 2 , width , precision - 2 )
        return fmt2 % ( v , eh , el ) , None 
    elif 10  <= av < 100  :
        fmt1  = '( %%+%d.%df +/%%-%d.%df -/%%-%d.%df )' %  ( width , precision - 1 , width , precision - 1 , width , precision - 1 )
        return fmt1 % ( v , eh , el ) , None 
    elif 1   <= av < 10   :
        fmt0  = '( %%+%d.%df +/%%-%d.%df -/%%-%d.%df )' %  ( width , precision     , width , precision     , width , precision     )
        return fmt0 % ( v , eh , el ) , None 

    from  ostap.math.base        import frexp10 
    v_a , v_e = frexp10 ( av )

    v  /= 10**(v_e-1)
    eh /= 10**(v_e-1)
    el /= 10**(v_e-1)
    
    v_e -= 1     
    n , r = divmod  ( v_e , 3 )    
    if 0 != r : 
        r -= 3
        n += 1

    v  *= 10**r
    eh *= 10**r 
    el *= 10**r 

    fmt0  = '( %%+%d.%df +/%%-%d.%df -/%%-%d.%df )' %  ( width , precision     , width , precision     , width , precision     )
    return fmt0 % ( v , eh , el ) , 3 * n


# =============================================================================
## format list of strings into multicolumn string
#  @code 
#  >>> strings =  ....
#  >>> table   = multicolumn (  strings , indent = 2 )
#  >>> print table
#  @endcode 
def multicolumn ( lines , term_width=None , indent = 0 , pad = 2 ):
    """Format list of strings into multicolumn string
    >>> strings =  ....
    >>> table   = multicolumn (  strings , indent = 2 )
    >>> print table 
    """
    n_lines = len(lines)
    if n_lines == 0:
        return
    
    if not term_width :
        from ostap.utils.basic import terminal_size 
        h , term_width = terminal_size()
        
    col_width = max(len(line) for line in lines)
    n_cols = int((term_width + pad - indent)/(col_width + pad))
    n_cols = min(n_lines, max(1, n_cols))
    
    col_len = int(n_lines/n_cols) + (0 if n_lines % n_cols == 0 else 1)
    if (n_cols - 1) * col_len >= n_lines:
        n_cols -= 1
        
    cols = [lines[i*col_len : i*col_len + col_len] for i in range(n_cols)]
    
    rows        = list(zip(*cols))
    rows_missed = list(zip(*[col[len(rows):] for col in cols[:-1]]))
    rows.extend(rows_missed)

    result = []
    for row in rows:
        line = " "*indent + (" "*pad).join(line.ljust(col_width) for line in row)
        result.append ( line )
    return '\n'.join ( result )


# =======================================================================================
## @class DisplayTree
#  Very simple class to allow a rendering of Tree-like objects,
#  in particular the structure and the content of directories 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date 2020-01-029
class DisplayTree ( object ) :
    """Very simple class to allow a rendering of Tree-like objects,
    in particular the structure and the content of directories 
    """    
    prefix_item_middle   = '\033(0\x74\033(B' + '\033(0\x71\033(B' + '\033(0\x71\033(B'
    prefix_item_last     = '\033(0\x6d\033(B' + '\033(0\x71\033(B' + '\033(0\x71\033(B'
    prefix_parent_middle = '    '  
    prefix_parent_last   = '\033(0\x78\033(B' +  '   '


    def __init__  ( self            ,
                    payload         ,   ## the object 
                    parent  = None  ,   ## parent if any  
                    display = None  ,   ## display function: how to display it? 
                    isdir   = False ,   ## directory object ?
                    last    = False ) : ## last in the list? 
        
        self.__payload = payload
        self.__parent  = parent

        if   display :         ## use display function if specified 
            self.__display = display
        elif parent  :         ## otherwise pick if from the parent 
            self.__display = parent.__display
            
        self.__last    = last
        self.__isdir   = isdir        
        self.__depth   = self.parent.depth + 1 if parent else 0 

    @property
    def payload ( self ) :
        """``payload''  : the actual object, hold by the tree leaf"""
        return self.__payload
    @property
    def parent ( self ) :
        """``parent'' : the parent element in the tree"""
        return self.__parent
    @property
    def last   (  self ) :
        """``last''  : is it a alst object oin the list? """
        return self.__last
    @property
    def isdir  (  self ) :
        """``isdir''  : is it `directory-like' item? """
        return self.__isdir    
    @property
    def depth  (  self ) :
        """``depth''  : how deep is our tree? """
        return self.__depth 
    
    @property 
    def itemname ( self ) :
        """``itemname'' : how the name of the leaf is displayed?"""
        return self.__display ( self.payload , self.isdir )

    # ==========================================================================
    ##  show the (sub)tree  
    def showme ( self , prefix = '' ) :
        """Show the constructed (sub)tree  
        """        
        if self.parent is None:
            return self.itemname

        symbols = self.prefix_item_last if self.last else self.prefix_item_middle

        graph   = [ prefix + '{!s} {!s}'.format ( symbols , self.itemname ) ]

        parent = self.parent        
        while parent and parent.parent is not None:
            pp     = self.prefix_parent_middle if parent.last else self.prefix_parent_last
            graph.append  ( pp )
            parent = parent.parent

        return ''.join ( reversed ( graph ) )

    def __str__ (  self ) :
        return 'Leaf(%s,isdir=%s,last=%s)' % ( self.itemname ,
                                               self.isdir    ,
                                               self.last     ) 
    __repr__ = __str__
    
# =============================================================================
if '__main__' == __name__ :
    
    from ostap import banner
    logger.info ( __file__  + '\n' + banner )
    logger.info ( 80*'*'   )
    logger.info ( __doc__  )
    logger.info ( 80*'*' )
    logger.info ( ' Author  : %s' %         __author__    ) 
    logger.info ( ' Version : %s' %         __version__   ) 
    logger.info ( ' Date    : %s' %         __date__      )
    logger.info ( ' Symbols : %s' %  list ( __all__     ) )
    logger.info ( 80*'*' ) 
    
# =============================================================================
# The END 
# =============================================================================
