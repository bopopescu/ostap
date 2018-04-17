#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file chopping.py
#  ``TMVA Chopper'' - helper utility to train/use  TMVA using ``chopping''
#
# The most frequest case:
# - TMVA is trained using the simulated events as ``Signal'' and realtively
# limited sample of data events (e.g. sidebands)  as ``Backrgound''.
# To avoid using the same backrgound events for training and the final evaluation,
# ``background'' sample is split into ``N'' independent categories and
# ``N''-independent TMVA trainings are performed.
# - For each training the corresponding category of backroung events is
# not used for this training.
# - For the final TMVA evaluation, for the events from category ``i''
# the corresponding trained TMVA is used [By construction,  these events have
# not been used for the training of corresponding TMVA].
# 
# @attention For the large number of categories ``N'' it could be rather slow,
#            since too many TMVA's need to be trained)
#
# The interface is very similaer to TMVATrainer/TMVAReader, but one needs to specify
#  -  For training:
#  * <code>N</code>: number of categories 
#  * <code>category</code>: the string/expression with TTree variables
#                           that used to construct the category,
#                            e.g.  <code>'event'</code>. The actual expression used
#                            to get the category number is constructed as 
#                             <code>'(category)%N'</code>
#  - For reading
#  * <code>N</code> must be the same as above
#  * <code>categoryfunc</code>: python callable that gets category number, e.g.
#    <code>categoryfunc = lambda s : int(s.event)%N </code>
#
#  @author Vanya BELYAEV Ivan.Belyaeve@itep.ru
#  @date 2017-09-10
# =============================================================================
"""``TMVAChopper'' - helper utility to train/use  TMVA using ``chopping''
Most frequest case:

TMVA is trained using the simulated events as ``Signal'' and realtively
limited sample of data events (e.g. sidebands)  as ``Backrgound''.
To avoid using the same backrgound events for training and the final evaluation,
``background'' sample is split into ``N'' independent categories and
``N''-independent TMVA trainings are performed.
For each training the corresponding category of backroung events is not
used for this training.
For the final TMVA evaluation, for the events from category ``i'' the corresponding
trained TMVA is used [By construction,  these events have not been used for
the training of corresponding TMVA].

- For the large number of categories it coudol be rather slow, since too many
TMVA's need to be trained

The interface is very similar to TMVATrainer/TMVAReader, but one needs to specify:

-  For training:
*  N        : number of categories 
*  category : the string/expression with TTree variables 
that used to construct the category, e.g.  'event'.

The actual expression used to get the category number is constructed as '(category)%N'

- For reading
* N            :   number of  categories (must be the same as above)
* categoryfunc : python callable that gets category number from TTree, e.g.: 

>>> N = 10 
>>> categoryfunc = lambda s : int(s.event)%N 

"""
# =============================================================================
__version__ = "$Revision:"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2017-09-10"
__all__     = (
    ##
    "Trainer"              , ## the ``chopper'' trainer for TMVA 
    "Reader"               , ## the ``chopper'' reader  for TMVA
    'addChoppingResponse'  , ## add ``chopping'' response to RooDataSet
    )
# =============================================================================
import ROOT
from ostap.logger.logger import getLogger
if '__main__' ==  __name__ : logger = getLogger ( 'ostap.tools.chopping' )
else                       : logger = getLogger ( __name__               )
# =============================================================================
from   ostap.tools.tmva   import Trainer as TMVATrainer
from   ostap.tools.tmva   import Reader  as TMVAReader
from   ostap.core.pyrouts import hID, h1_axis 
import ostap.trees.trees 
import ostap.trees.cuts
import ostap.utils.utils  as Utils 
# =============================================================================
## @class Trainer
#  The ``chopping''  trainer. Th einterface is very similar to TMVA Trainer
#  with two   additional mandatory parameters:
#  -  <code>N</code>        : number of categories 
#  -  <code>category</code> : the string/expression with TTree variables 
#  that used to construct the category, e.g.
#  <code>'event'</code> or <code>'137*event+813*run'</code> or 
#  The actual expression used to get the category number is constructed as
#  <code>'(category)%N'</code>
#
# - Book the trainer
# @code 
# >>> N = 11 
# >>> trainer = Trainer (
# ... category = '137*evt+813*run' ,
# ... N        = N                 , 
# ... methods =  [ # type                   name   configuration
# ...      ( ROOT.TMVA.Types.kMLP        , 'MLP'        , 'H:!V:EstimatorType=CE:VarTransform=N:NCycles=200:HiddenLayers=N+3:TestRate=5:!UseRegulator' ) ,
# ...      ( ROOT.TMVA.Types.kBDT        , 'BDTG'       , 'H:!V:NTrees=100:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2' ) , 
# ...      ( ROOT.TMVA.Types.kCuts       , 'Cuts'       , 'H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart' ) ,
# ...      ( ROOT.TMVA.Types.kFisher     , 'Fisher'     , 'H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10' ),
# ...      ( ROOT.TMVA.Types.kLikelihood , 'Likelihood' , 'H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50' ) ] ,
# ... variables  = [ 'var1' , 'var2' ,  'var3' ] ,  ## Variables to use in the training
# ... signal     = signal_tree      , ## TTree/TChain with ``signal'' sample   
# ... background = background_tree  , ## TTree/TChain with ``background'' sample   
# ... name       = 'TMVAChopper'    ,
# ... verbose    = False )
# @endcode
#
# - Use the trainer
# @code
# >>> trainer.train()
# @endcode
# 
# - Get  results from the  trainer
# @code
# >>> weights_files = trainer.weights_files ## weights files (XML) 
# >>> class_files   = trainer.  class_files ## class files (C++)
# >>> output_files  = trainer. output_files ## output ROOT files 
# >>> tar_file      = trainer.    tar_file  ## tar-file (XML&C++)
# @endcode
class Trainer(object) :
    """The ``chopping''  trainer. Th einterface is very similar to TMVA Trainer
    with two   additional mandatory parameters:
    1. ``N''        : number of categories 
    2. ``category'' : the string/expression with TTree variables 
    that used to construct the category, e.g.  'event'.
    The actual expression used to get the category number is constructed as
    '(category)%N'

    - Book the trainer: 
    >>> N = 11 
    >>> trainer = Trainer (
    ... category = '137*evt+813*run' ,
    ... N        = N                 , 
    ... methods =  [ # type                   name   configuration
    ...      ( ROOT.TMVA.Types.kMLP        , 'MLP'        , 'H:!V:EstimatorType=CE:VarTransform=N:NCycles=200:HiddenLayers=N+3:TestRate=5:!UseRegulator' ) ,
    ...      ( ROOT.TMVA.Types.kBDT        , 'BDTG'       , 'H:!V:NTrees=100:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2' ) , 
    ...      ( ROOT.TMVA.Types.kCuts       , 'Cuts'       , 'H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart' ) ,
    ...      ( ROOT.TMVA.Types.kFisher     , 'Fisher'     , 'H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10' ),
    ...      ( ROOT.TMVA.Types.kLikelihood , 'Likelihood' , 'H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50' ) ] ,
    ... variables  = [ 'var1' , 'var2' ,  'var3' ] ,  ## Variables to use in the training
    ... signal     = signal_tree      , ## TTree/TChain with ``signal'' sample   
    ... background = background_tree  , ## TTree/TChain with ``background'' sample   
    ... name       = 'TMVAChopper'    ,
    ... verbose    = False )

    - Use the trainer
    >>> trainer.train()

    - Get  results from the  trainer
    >>> weights_files = trainer.weights_files ## weights files (XML) 
    >>> class_files   = trainer.  class_files ## class files (C++)
    >>> output_files  = trainer. output_files ## output ROOT files 
    >>> tar_file      = trainer.    tar_file  ## tar-file (XML&C++)
    """
    def __init__ ( self                              ,
                   category                          ,   ## accessor to category 
                   N                                 ,   ## number of categories 
                   methods                           ,   ## list of TMVA methods
                   variables                         ,   ## list of variables 
                   signal                            ,   ## signal tree
                   background                        ,   ## background tree
                   signal_cuts       = ''            ,   ## signal cuts 
                   background_cuts   = ''            ,   ## background cuts 
                   spectators        = []            ,
                   bookingoptions    = "Transformations=I;D;P;G,D" , 
                   configuration     = "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" ,
                   signal_weight     = None          ,                
                   background_weight = None          ,                                     
                   name              = 'TMVAChopper' ,   ## the name 
                   verbose           = False         ,   ## verbose ? 
                   chop_signal       = False         ,   ## chop the signal     ?
                   chop_background   = True          ) : ## chop the background ?
        """Create TMVA ``chopping'' trainer
        
        >>> N = 11 
        >>> trainer = Trainer (
        ... category = '137*evt+813*run' ,
        ... N        = N                 , 
        ... methods =  [ # type                   name   configuration
        ...      ( ROOT.TMVA.Types.kMLP        , 'MLP'        , 'H:!V:EstimatorType=CE:VarTransform=N:NCycles=200:HiddenLayers=N+3:TestRate=5:!UseRegulator' ) ,
        ...      ( ROOT.TMVA.Types.kBDT        , 'BDTG'       , 'H:!V:NTrees=100:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=2' ) , 
        ...      ( ROOT.TMVA.Types.kCuts       , 'Cuts'       , 'H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart' ) ,
        ...      ( ROOT.TMVA.Types.kFisher     , 'Fisher'     , 'H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10' ),
        ...      ( ROOT.TMVA.Types.kLikelihood , 'Likelihood' , 'H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50' ) ] ,
        ... variables  = [ 'var1' , 'var2' ,  'var3' ] ,  ## Variables to use in the training
        ... signal     = signal_tree      , ## TTree/TChain with ``signal'' sample   
        ... background = background_tree  , ## TTree/TChain with ``background'' sample   
        ... name       = 'TMVAChopper'    ,
        ... verbose    = False )
        
        """
        assert isinstance ( N , (int,long) ) and 1 < N , "Invalid number of categories"

        self.__chop_signal     = True if chop_signal     else False 
        self.__chop_background = True if chop_background else False 

        assert  self.__chop_signal or self.__chop_background, "Neither signal nor background chopping" 
        
        self.__category  = category 
        self.__N         = N

        self.__signal            = signal     
        self.__background        = background 

        self.__methods           = tuple(methods) 
        self.__signal_weight     = signal_weight 
        self.__signal_cuts       = ROOT.TCut ( signal_cuts )     
        
        self.__background_weight = background_weight 
        self.__background_cuts   = ROOT.TCut ( background_cuts ) 
        
        self.__variables         = tuple(variables)
        self.__spectators        = tuple(spectators)

        self.__bookingoptions    = bookingoptions
        self.__configuration     = configuration
        
        self.__name              = name
        self.__verbose           = True if verbose else False 

        self.__sig_histos        = ()
        self.__bkg_histos        = ()
        
        
        cat = '(%s)%%%d' % ( self.category , self.N  )
        
        if self.chop_signal      :
            hs1 = ROOT.TH1F( hID() , 'Signal categories' , self.N * 5 , -0.5 , self.N - 1 ) 
            hs2 = h1_axis ( [ -0.5+i for i in range(   self.N + 1 ) ] , title = hs1.GetTitle() ) 
            self.signal.project     ( hs1 , cat , self.signal_cuts )
            self.signal.project     ( hs2 , cat , self.signal_cuts )
            self.__sig_histos = hs1,hs2
            st = hs2.stat()
            if 0 >=  st.min()  : logger.warning ("Some signal categories are empty!")                 
            logger.info('Signal     category population mean/rms: %s/%s' % ( st.mean() , st.rms() ) )
                        
        if self.chop_background  :
            hb1 = ROOT.TH1F( hID() , 'Background categories' , self.N * 5 , -0.5 , self.N - 1 ) 
            hb2 = h1_axis ( [ -0.5+i for i in range(   self.N + 1 ) ] , title = hb1.GetTitle() ) 
            self.background.project ( hb1 , cat , self.background_cuts )
            self.background.project ( hb2 , cat , self.background_cuts )
            self.__bkg_histos = hb1,hb2
            ##
            st = hb2.stat()
            if 0 >=  st.min()  : logger.warning ("Some background categories are empty!")                 
            logger.info('Background category population mean/rms: %s/%s' % ( st.mean() , st.rms() ) )


        ##  trick to please Kisa 
        from ostap.trees.trees import Chain
        self.__signal            = Chain ( signal     ) 
        self.__background        = Chain ( background )  

        ## book the trainers 
        self.__trainers      = () 
        self.__weights_files = []
        self.__class_files   = []
        self.__output_files  = []
        self.__tar_file      = None 
        self.__log_file      = None 

    ## create all trainers 
    def __create_trainers ( self ) :
        if self.trainers : logger.debug ('Remove existing trainers ')
        self.__trainers = [] 
        for i in  range ( self.N ) : self.__trainers.append ( self.create_trainer ( i ) )
        self.__trainers = tuple ( self.__trainers ) 

    ## create the trainer for category "i"
    def create_trainer ( self , i , verbose = True ) :
        """Create the trainer for category ``i''
        """
        cat       = '(%s)%%%d' % ( self.category , self.N  )
        nam       =  '%s_%03d' % ( self.name , i )
        scuts     = self.    signal_cuts 
        bcuts     = self.background_cuts 
        icategory = "(%s)!=%d" % ( cat , i ) 
        if self.chop_signal     :
            scuts = icategory * scuts if scuts else icategory
        if self.chop_background :
            bcuts = icategory * bcuts if bcuts else icategory
            
        t = TMVATrainer ( methods           = self.methods           ,
                          variables         = self.variables         ,
                          signal            = self.signal            ,
                          background        = self.background        ,
                          spectators        = self.spectators        ,
                          bookingoptions    = self.bookingoptions    ,
                          configuration     = self.configuration     ,
                          signal_weight     = self.signal_weight     ,
                          background_weight = self.background_weight ,
                          output_file       = ''      , 
                          ##
                          signal_cuts       = scuts   , 
                          background_cuts   = bcuts   ,
                          ##
                          name              = nam     ,
                          verbose           = verbose )
        return t 

    @property
    def name    ( self ) :
        """``name''    : the name of TMVA chopper"""
        return self.__name
    
    @property
    def trainers ( self ) :
        """``trainers'' - the  actual list of N-TMVA  trainers for N-categories"""
        return self.__trainers 

    @property
    def category ( self ) :
        """``category'' -  the accessor(string) to the category"""
        return self.__category 

    @property
    def N        ( self ) :
        """``N'' - number of categories for chopping"""
        return self.__N

    @property
    def chop_signal ( self ) :
        """``chop_signal'' : use chopping for signal?"""
        return self.__chop_signal
    
    @property
    def chop_background ( self ) :
        """``chop_background'' : use chopping for background?"""
        return self.__chop_background
    
    @property
    def methods ( self ) :
        """``methods'' : the list of TMVA methods to be used"""
        return tuple(self.__methods)
    
    @property
    def variables ( self ) :
        """``variables'' : the list of variables  to be used for training"""
        return tuple(self.__variables)

    @property
    def spectators ( self ) :
        """``spectators'' : the list of spectators to be used"""
        return tuple(self.__spectators)

    @property
    def signal ( self ) :
        """``signal'' :  TTree for signal events"""
        return self.__signal
    
    @property
    def signal_cuts ( self ) :
        """``signal_cuts'' :  cuts to be applied for ``signal'' sample"""
        return ROOT.TCut(self.__signal_cuts)

    @property
    def signal_weight ( self ) :
        """``signal_weight'' : weight to be applied for ``signal'' sample"""
        return self.__signal_weight
 
    @property
    def background ( self ) :
        """``background'' :  TTree for background events"""
        return self.__background
    
    @property
    def background_cuts ( self ) :
        """``background_cuts'' :  cuts to be applied for ``backgroud'' sample """
        return ROOT.TCut(self.__background_cuts)
    
    @property
    def background_weight ( self ) :
        """``background_weight'' : weight to be applied for ``background'' sample"""
        return self.__background_weight

    @property
    def bookingoptions ( self ) :
        """``bookingoptions'' : options used to book TMVA::Factory"""
        return str(self.__bookingoptions)
    
    @property
    def configuration ( self ) :
        """``configuration'' : options used to book TMVA"""
        return str(self.__configuration)
    
    @property
    def verbose ( self ) :
        """``verbose'' : verbosity  flag"""
        return self.__verbose

    @property
    def signal_categories ( self ) :
        """``signal_categories'' - two histograms(different binning) with signal category population"""
        return self.__sig_histos
    @property
    
    def background_categories ( self ) :
        """``background_categories'' - two histograms(different binning) with background category population"""
        return self.__bkg_histos
    
    @property
    def weights_files ( self ) :
        """``weights_files'': the list/tuple of final files with TMVA weights"""
        return tuple(self.__weights_files)
    @property
    def class_files ( self ) :
        """``class_files'' : the list/tuple of final files with TMVA classes"""
        return tuple(self.__class_files)
    @property
    def output_files ( self ) :
        """``output_files'': the output files """
        return tuple(self.__output_files)

    @property
    def tar_file ( self ) :
        """``tar_file'': the compressed tar file"""
        return str(self.__tar_file) if self.__tar_file else None
    
    @property
    def log_file ( self ) :
        """``log_file'': the compressed tar file with tarinng log-files"""
        return str(self.__log_file) if self.__log_file else None 

    # =========================================================================
    ## The main method: training of all subsamples 
    #  - Use the trainer
    # @code 
    # >>> trainer.train()
    # @endcode
    #
    # - Get  results from the  trainer
    # @code
    # >>> weights_files = trainer.weights_files ## weights files (XML) 
    # >>> class_files   = trainer.  class_files ## class files (C++)
    # >>> output_files  = trainer. output_files ## output ROOT files 
    # >>> tar_file      = trainer.    tar_file  ## tar-file (XML&C++)
    # @endcode
    def train ( self ) :
        """The main method: training of all subsamples
        - Use the trainer
        >>> trainer.train()
        
        - Get  results from the  trainer
        >>> weights_files = trainer.weights_files ## weights files (XML) 
        >>> class_files   = trainer.  class_files ## class files (C++)
        >>> output_files  = trainer. output_files ## output ROOT files 
        >>> tar_file      = trainer.    tar_file  ## tar-file (XML&C++)
        """
        ## create the trainers 
        self.__create_trainers()

        assert 1<= self.N and self.N == len ( self.trainers ), 'Invalid trainers!'
        
        weights  = []
        classes  = []
        outputs  = [] 
        tarfiles = [] 
        logfiles = [] 
        for  t in self.trainers :
            logger.info  ( "Trainer(%s): train the trainer ``%s''" % ( self.name , t.name ) ) 
            t.train() 
            weights  += [ t.weights_files ] 
            classes  += [ t.  class_files ] 
            outputs  += [ t. output_file  ] 
            tarfiles += [ t.    tar_file  ] 
            logfiles += [ t.    log_file  ] if t.log_file else [] 

        self.__weights_files = tuple ( weights ) 
        self.__class_files   = tuple ( classes )
        self.__output_files  = tuple ( outputs )

        self.make_tarfile ( tarfiles , logfiles )

        logger.debug ( "Trainer(%s): Class   files : %s" % ( self.name , self.  class_files ) ) 
        logger.debug ( "Trainer(%s): Weights files : %s" % ( self.name , self.weights_files ) )
        logger.info  ( "Trainer(%s): Output  files : %s" % ( self.name , self. output_files ) ) 
        logger.info  ( "Trainer(%s): Tar     file  : %s" % ( self.name , self.    tar_file  ) )
        if self.log_file : 
            logger.info  ( "Trainer(%s): Log/tgz file  : %s" % ( self.name , self. log_file ) ) 


        return self.__weights_files 

    ## create the tarfile from the list of tarfiles 
    def make_tarfile ( self , tarfiles , logfiles = [] ) : 
    
        import tarfile, os
        
        tfile = self.name + '.tgz'
        if os.path.exists ( tfile ) :
            logger.debug  ( "Trainer(%s): Remove existing tar-file %s" % ( self.name , tfile ) )
            
        with tarfile.open ( tfile , 'w:gz' ) as tar :
            for x in  tarfiles: tar.add ( x )
            logger.debug ( "Trainer(%s): Tar/gz    file  : %s" % ( self.name , tfile ) ) 
            if self.verbose : tar.list ()

        ## finally set the tar-file 
        if os.path.exists ( tfile ) and tarfile.is_tarfile( tfile ) :
            self.__tar_file = tfile

        if not logfiles : return tfile
        
        lfile = self.name + '_logs.tgz'
        if os.path.exists ( lfile ) :
            logger.debug  ( "Trainer(%s): Remove existing tar-logfile %s" % ( self.name , lfile ) )

        with tarfile.open ( lfile , 'w:gz' ) as tar :
            for x in  logfiles: tar.add ( x )
            logger.debug ( "Trainer(%s): Tar/gz logfile  : %s" % ( self.name , lfile ) ) 
            if self.verbose : tar.list ()
            
        ## finally set the tar-file 
        if os.path.exists ( lfile ) and tarfile.is_tarfile( lfile ) :
            self.__log_file = lfile 
            
        return tfile

    # =======================================================================
    ## use the parallel training 
    def ptrain ( self , log = True , silent = True ) :
        """Use the parallel training
        """
        from ostap.parallel.kisa import ChopperTraining, WorkManager

        import sys 
        task   = ChopperTraining()
        wmgr   = WorkManager ( silent = False )
        params = [ ( i , self , log , silent ) for i in range ( self.N ) ]

        sys.stdout.flush()
        sys.stderr.flush()
        
        wmgr.process( task, params )

        sys.stdout.flush()
        sys.stderr.flush()

        assert self.N == len(task.output[0]), 'Invalid number of weights files '
        assert self.N == len(task.output[1]), 'Invalid number of   class files '
        assert self.N == len(task.output[2]), 'Invalid number of  output files '
        assert self.N == len(task.output[3]), 'Invalid number of     tar files '
        assert self.N == len(task.output[4]), 'Invalid number of     log files '
        
        weights  = [ i[1] for i in task.output[0]         ]
        classes  = [ i[1] for i in task.output[1]         ]
        outputs  = [ i[1] for i in task.output[2]         ]
        tarfiles = [ i[1] for i in task.output[3]         ]
        logfiles = [ i[1] for i in task.output[4] if i[1] ]
        
        self.__weights_files = tuple ( weights ) 
        self.__class_files   = tuple ( classes )
        self.__output_files  = tuple ( outputs )
        
        self.make_tarfile ( tarfiles , logfiles )

        logger.debug ( "Trainer(%s): Class   files : %s" % ( self.name , self.  class_files ) ) 
        logger.debug ( "Trainer(%s): Weights files : %s" % ( self.name , self.weights_files ) )
        logger.info  ( "Trainer(%s): Output  files : %s" % ( self.name , self. output_files ) ) 
        logger.info  ( "Trainer(%s): Tar     file  : %s" % ( self.name , self.    tar_file  ) ) 
        if self.log_file :
            logger.info  ( "Trainer(%s): Log/tgz file  : %s" % ( self.name , self. log_file ) ) 
            
        return self.__weights_files 
        
# =============================================================================
## @class WeightFiles
#  helper structure  to deal with weights files
import ostap.utils.utils as Utils 
class WeightsFiles(Utils.CleanUp) :
    """Helper structure  to deal with weights files
    """
    def __init__ ( self , weights_files ) :
        
        if isinstance ( weights_files , str  ) :
            
            wf  = weights_files
            import tarfile, os
            assert os.path.exists  ( wf ) and tarfile.is_tarfile ( wf ) , "Non-existing or invalid tarfile %s "  % wf
            
            with tarfile.open ( wf , 'r' ) as tar :
                logger.debug ( "Open tarfile %s" % wf )
                ## tar.list()
                tmpdir = self.tmpdir 
                tar.extractall ( path = tmpdir )                
                logger.debug ('Un-tar into temporary directory %s' % tmpdir ) 
                weights_files  = [ os.path.join ( tmpdir , i ) for i in tar.getnames() ]
                self.tmpfiles += weights_files
                
        self.__weights_files = weights_files

    @property
    def files   ( self ) :
        "``files'': the weigths file"
        import copy
        return copy.deepcopy ( self.__weights_files ) 
# =============================================================================
## @class Reader
#  The ``chopping'' TMVA reader.
#  The interface is very similar to TMVA Trainer
#  with two   additional mandatory parameters:
#  - <code>N</code>           : number of categories (must be the  same as for training) 
#  - <code>categoryfunc</code>: python callable that gets category number from TTree, e.g.:
#  @code 
#  >>> N = 11 
#  >>> categoryfun = lambda s : int(137*s.evt+813*s.run)%N
#  @endcode
#
# - Book the reader
# @code 
# >>> reader = Reader ( 
# ...    name          = 'CHOPPER' ,
# ...    categoryfunc  = categoryfun 
# ...    N             = N         ,
# ...    variables     = [ ('var1' , lambda s : s.var1 )   ,
# ...                      ('var2' , lambda s : s.var2 )   ,
# ...                      ('var3' , lambda s : s.var3 ) ] ,
# ...     weights_files = weights_files  )
# @endcode
# 
# Here <code>weights_files</code> can be :
# - single tar/tgz/tar.gz-file with weights files (output from <code>Trainer.tar_file</code>)
# - the structure of xml-files with weights       (output from <code>Trainer.weights_files</code>)
#
# - Use the reader
# @code 
# >>> tree =  ....  ## TTree/TChain/RooDataSet with data
# >>> for entry in tree :
# ...     mlp  = reader ( 'MLP'  , entry )  ## evaluate MLP-TMVA
# ...     bdtg = reader ( 'BDTG' , entry )  ## evalaute BDTG-TMVA
# ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   
# @endcode 
#
# - A bit more efficient form is :
# @code 
# >>> tree =  ....  ## TTree/TChain/RooDataSet with data
# >>> mlp_fun  =  reader.MLP
# >>> bdgt_fun =  reader.BDTG
# >>> for entry in tree :
# ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
# ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
# ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)
# @endcode 
# - It it natually merges with Ostap's <code>SelectorWithVars</code> utility
class Reader(object) :
    """The ``chopping'' TMVA reader.
    The interface is very similar to TMVA Trainer
    with two   additional mandatory parameters:
    1. ``N''           : number of categories (must be the  same as for training) 
    2. ``categoryfun'' : python callable that gets category number from TTree, e.g.:

    >>> N = 11 
    >>> categoryfun = lambda s : int(137*s.evt+813*s.run)%N

    - Book the reader:
    >>> reader = Reader ( 
    ...    name          = 'CHOPPER' ,
    ...    categoryfunc  = categoryfun 
    ...    N             = N         ,
    ...    variables     = [ ('var1' , lambda s : s.var1 )   ,
    ...                      ('var2' , lambda s : s.var2 )   ,
    ...                      ('var3' , lambda s : s.var3 ) ] ,
    ..     weights_files = weights_files  )
    
    ``weights_files'' can be :
    - single tar/tgz/tar.gz-file with weights files (output from ``Trainer.tar_file'')
    - the structure of xml-files with weights       (output from ``Trainer.weights_files'')
    
    - Use the reader
    >>> tree =  ....  ## TTree/TChain/RooDataSet with data
    >>> for entry in tree :
    ...     mlp  = reader ( 'MLP'  , entry )  ## evaluate MLP-TMVA
    ...     bdtg = reader ( 'BDTG' , entry )  ## evalaute BDTG-TMVA
    ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   

    - A bit more efficient form is :
    >>> tree =  ....  ## TTree/TChain/RooDataSet with data
    >>> mlp_fun  =  reader.MLP
    >>> bdgt_fun =  reader.BDTG
    >>> for entry in tree :
    ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
    ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
    ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)
    
    - It it natually merges with Ostap's ``SelectorWithVars'' utility     
    """
    def __init__ ( self                           ,
                   categoryfunc                   ,
                   N                              , 
                   variables                      ,
                   weights_files                  , 
                   name         = 'ChopperReader' ,
                   options      = ''              ,
                   verbose      = False           ) :
        """ Book the reader:
        >>> reader = Reader ( 
        ...    name          = 'CHOPPER' ,
        ...    categoryfunc  = categoryfun 
        ...    N             = N         ,
        ...    variables     = [ ('var1' , lambda s : s.var1 )   ,
        ...                      ('var2' , lambda s : s.var2 )   ,
        ...                      ('var3' , lambda s : s.var3 ) ] ,
        ..     weights_files = weights_files  )
        
        ``weights_files'' can be :
        - single tar/tgz/tar.gz-file with weights files (output from ``Trainer.tar_file'')
        - the structure of xml-files with weights       (output from ``Trainer.weights_files'')
        """
        assert isinstance ( N , (int,long) ) and 1 <= N , "``N'' is illegal %s/%s"  % ( N , type(N) )

        self.__name          = str(name) 
        self.__categoryfunc  = categoryfunc, 
        self.__N             = N
        self.__variables     = tuple(variables)
        self.__methods       = []

        import copy
        files = WeightsFiles ( weights_files ).files 
        self.__weights_files = copy.deepcopy( files)
        assert len ( self.weights_files ) == N , "Invalid length of ``weights_files''"

        self.__readers   = []
        for i in range ( self.N ) :

            inam = '%s_%03d'   % ( self.name , i )
            
            self.__readers.append ( TMVAReader ( name          = inam                  ,
                                                 variables     = self.variables        ,
                                                 weights_files = self.weights_files[i] ,
                                                 options       = options               ,
                                                 verbose       = verbose               ) )
                
        self.__readers  = tuple   ( self.__readers )
        self.__histo    = h1_axis ( [ -0.5 + i for i in range ( self.N + 1 ) ] ,
                                    title ="Category population" )

        for r in self.__readers :
            mr = list ( r.methods )
            if not self.__methods : self.__methods = mr
            m1 = set ( mr )
            m2 = set ( self.__methods ) 
            assert m1 == m2 , "Inconsistent configuration of readers is detected"

        self.__methods = tuple (  self.__methods ) 
            
    @property
    def name ( self ) :
        """```name'' - the name of Chopper Reader"""
        return self.__name

    @property
    def N ( self ) :
        """```N'' - number of categories"""
        return self.__N
     
    @property
    def methods ( self ) :
        """``methods'' - the list/tuple of booked TMVA methods"""
        return tuple (self.__methods ) 

    @property
    def variables ( self ) :
        """```variables'' - the list variables with accessor functions, e.g.
        >>> variables = [ ## name      accessor  
        ...              ( 'pt'   , lambda s : s.pt ) ,
        ...              ( 'ip'   , lambda s : s.ip ) ,
        ...                'var1'                     ,   ## s.var1 will be used 
        ...                'var2'                     ] , ## s.var2 will be used 
        """
        return self.__variables
    
    @property
    def weights_files( self ) :
        """```weight_files'' - TMVA weight files"""
        return tuple(self.__weights_files)
       
    @property
    def readers ( self ) :
        """``readers'' -  the actual list/tuple of readers"""
        return self.__readers

    @property
    def categoryfunc ( self ) :
        """``categoryfunc'' - the actual callable for the category classification, 
        e.g. for 11 categories:
        >>> categoryfun = lambda s : int(137*s.evt+813*s.run)%11          
        """
        return self.__categoryfunc[0]

    @property
    def histo ( self ) :
        """``histo'': histogram with the category populations statistic"""
        return self.__histo 

    # =========================================================================
    ## Helper class to get the decision of ``chopper''
    #  @code 
    #  reader = ...
    #  var = reader[ method ]
    #  val = var ( entry )
    #  @code
    class Method(TMVAReader.Var) :
        """Helper class to get the decision of ``chopper''
        >>> reader = ...
        >>> var = reader[ method ]
        >>> val = var ( entry )
        """
        def __init__ ( self , reader , method ) :
            TMVAReader.Var.__init__ (  self ,   reader , method )
            self.__N = reader.N 
        # =====================================================================
        ## Evaluate the chopper 
        #  @code
        #  tree = ...
        #  method = reader.MLP
        #  print 'Responce %s' % method ( tree )
        #  @endcode
        #  or using categroy and parameters
        #  @code
        #  category  = 2
        #  pt , y, phi = ...
        #  print 'Responce %s' % method ( category , pt , y , phi )
        #  @endcode 
        def __call__ ( self , arg ,  *args ) :
            """Evaluate the chopper from TTree/TChain/RooAbsData:
            >>>tree = ...
            >>> method = reader.MLP
            >>> print 'Responce %s' % method ( tree )
            Using category and parameters
            >>> category  = 2
            >>> pt , y, phi = ...
            >>> print 'Responce %s' % method ( category , pt , y , phi )
            """
            if isinstance ( arg , int ) and args :
                category = arg
                return self.evaluate ( category , *args ) 
            return self.eval ( arg , *args )
        # =====================================================================
        ## Evaluate the method from parameters 
        # @code 
        # method       = ...
        # pt, eta, phi = 5 ,  3.0 , 0  ## variables
        # category     = 2 
        # print 'Response is %s'    % method.evaluate ( category , pt ,  eta , phi ) 
        # @endcode 
        def evaluate ( self , category , *args ) :
            """Evaluate the method from parameters 
            >>> method       = ...
            >>> pt, eta, phi = 5 ,  3.0 , 0  ## variables
            >>> category     = ...
            >>> print 'Response is %s'    % method.evaluate ( category ,  pt ,  eta , phi ) 
            """
            return self.reader.evaluate ( category , self.method , *args )

        # ====================================================================
        ## Get the  mean over all categories
        #  @code
        #  method = ...
        #  pt, eta, phi = 5 ,  3.0 , 0  ## variables
        #  print 'Mean  response is %s' % method.mean (  pt , eta , phi ) 
        #  @endcode
        def mean ( self , *args ) :
            """Get the  mean over all categories
            >>> method = ...
            >>> pt, eta, phi = 5 ,  3.0 , 0  ## variables
            >>> print 'Mean  response is %s' % method (  pt , eta , phi ) 
            """
            sum = 0.0
            for i in range(self.__N) : sum += self.evaluate ( i , *args )
            return sum / float ( self.__N ) 
        
        # ====================================================================
        ## Get the full statistic over all categories
        #  @code
        #  method = ...
        #  pt, eta, phi = 5 ,  3.0 , 0  ## variables
        #  print 'Response statistic is %s' % method.stat (  pt , eta , phi ) 
        #  @endcode        
        def stat ( self , *args ) :
            """ Get the full statistic over all categories
            >>> method = ...
            >>> pt, eta, phi = 5 ,  3.0 , 0  ## variables
            >>> print 'Response statistic is %s' % method.stat (  pt , eta , phi ) 
            """
            from ostap.stats.counters import SE
            se = SE()
            for i in range(self.__N) : se += self.evaluate ( i , *args )
            return se 
                        
    ## =======================================================================
    ## helper utility to  get the correspondig function from the  reader:
    #  @code 
    #  >>> tree =  ....  ## TTree/TChain/RooDataSet with data
    #  >>> mlp_fun  =  reader['MLP']  ## <-- here!
    #  >>> bdgt_fun =  reader['BDTG'] ## <-- here!
    #  >>> for entry in tree :
    #  ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
    #  ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
    #  ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)
    # @encode        
    def __getitem__ ( self , method ) :
        """Helper utility to  get the correspondig function from the  reader:
        - Use the reader
        >>> tree =  ....  ## TTree/TChain/RooDataSet with data
        >>> mlp_fun  =  reader['MLP']  ## <-- here! 
        >>> bdgt_fun =  reader['BDTG'] ## <-- here!
        >>> for entry in tree :
        ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
        ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
        ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   
        """
        if not method in self.__methods :
            return KeyError( 'No method %s is booked!' %  method )
        return Reader.Method  ( self , method )
    
    ## =======================================================================
    ## helper utility to  get the correspondig function from the  reader:
    #  @code 
    #  >>> tree =  ....  ## TTree/TChain/RooDataSet with data
    #  >>> mlp_fun  =  reader.MLP  ## <-- here! 
    #  >>> bdgt_fun =  reader.BDTG ## <-- here!
    #  >>> for entry in tree :
    #  ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
    #  ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
    #  ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)
    # @encode        
    def __getattr__ ( self , method ) :
        """Helper utility to  get the correspondig function from the  reader:
        - Use the reader
        >>> tree =  ....  ## TTree/TChain/RooDataSet with data
        >>> mlp_fun  =  reader.MLP  ## <-- here! 
        >>> bdgt_fun =  reader.BDTG ## <-- here!
        >>> for entry in tree :
        ...     mlp  = mlp_fun  ( entry )  ## evaluate MLP-TMVA
        ...     bdtg = bdtg_fun ( entry )  ## evalaute BDTG-TMVA
        ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   
        """                
        if not method in self.__methods :
            return AttributeError( 'No method %s is booked!' %  method )
        return Reader.Method  ( self , method ) 

    # =========================================================================
    ## the main method - evaluate of TMVA from the certain category reader 
    #  - Use the reader
    #  @code 
    #  >>> tree =  ....  ## TTree/TChain/RooDataSet with data
    #  >>> for entry in tree :
    #  ...     mlp  = reader ( 'MLP'  , entry )  ## evaluate MLP-TMVA
    #  ...     bdtg = reader ( 'BDTG' , entry )  ## evalaute BDTG-TMVA
    #  ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   
    #  @endcode 
    #  @attention it is *not* CPU efficient
    #  Ugly trick with arrays is needed due to some technical problems
    #  (actually TMVA reader needs the address of ``float''(in C++ sense) variable
    def __call__ ( self , method , entry , cut_efficiency = 0.90 ) :
        """The main method - evaluate of TMVA from the certain category reader 
        
        - Use the reader
        >>> tree =  ....  ## TTree/TChain/RooDataSet with data
        >>> for entry in tree :
        ...     mlp  = reader ( 'MLP'  , entry )  ## evaluate MLP-TMVA
        ...     bdtg = reader ( 'BDTG' , entry )  ## evalaute BDTG-TMVA
        ...     print 'MLP/BDTG for  this event are %s/%s' %  (mlp , bdtg)   
        """
        icatfunc = self.__categoryfunc[0]
        ic       = icatfunc ( entry )
                 
        assert isinstance ( ic , (int,long) ) and 0 <= ic < self.__N, \
               "Invalid ``category'' %s/%s" % ( ic ,  type ( ic ) )
        return self.__readers[ ic ] ( method ,  entry , cut_efficiency ) 
        
    # ========================================================================
    ## evaluate TMVA
    #  @code
    #  reader   = ...
    #  pt, y    = ...  ##
    #  category = ... 
    #  print 'MLP response is: ', reader.evaluate ( category , 'MLP' , pt , y )
    #  @endcode
    def evaluate ( self , category , method , *args ) :
        """Evaluate TMVA
        >>> reader = ...
        >>> pt, y  = ...  ##
        >>> print 'MLP response is: ', reader.evaluate ( category , 'MLP' , pt , y )
        """
        assert isinstance ( category , ( int , long ) ) and 0 <= category < self.__N, \
               "Invalid ``category'' %s/%s" % ( category ,  type ( category ) )
        return self.__readers[ category ].evaluate ( method , *args ) 
                                


# =============================================================================
## Helper function to add TMVA response into dataset
#  @code
#  tar_file = trainer.tar_file
#  dataset  = ...
#  inputs = [ 'var1' , 'var2' , 'var2' ]
#  dataset.addTMVAResponce (  inputs , tar_file , prefix = 'tmva_' )
#  @endcode 
def addChoppingResponse ( dataset                     ,
                          chopper                     ,
                          N                           ,
                          inputs                      ,
                          weights_files               ,
                          category_name = 'chopping'  , 
                          prefix        = 'tmva_'     ,                          
                          suffix        = '_response' ,
                          aux           = 0.9         ) :
    """
    Helper function to add TMVA  response into dataset
    >>> tar_file = trainer.tar_file
    >>> dataset  = ...
    >>> inputs = [ 'var1' , 'var2' , 'var2' ]
    >>> dataset.addTMVAResponce (  inputs , tar_file , prefix = 'tmva_' )
    """
    assert isinstance ( N , int ) and 1 < N < 10000 , 'Invalid "N" %s' % N
    
    if isinstance ( chopper , str ) :
        
        if chopper in dataset :
            chopper = getattr ( varset , chopper )
        else : 
            varset  = dataset.get()
            varlist = ROOT.RooArgList()
            for v in varset : varlist.add ( v )
            chopper = ROOT.RooFormulaVar( 'chopping' , chopper , varlist )
            logger.debug ( 'Create chopping function %s' %  chopper ) 

    assert isinstance ( chopper , ROOT.RooAbsReal ), 'Invalid choper type %s' % chopper 
        
    category = ROOT.RooCategory ( category_name ,
                                  'Chopping category: (%s)%%%d' %  ( chopper.GetTitle() , N ) ) 
    for i in range(N) :
        
        if   N <    10 : cn = category_name + '_%d'    % i
        if   N <   100 : cn = category_name + '_%02d'  % i
        elif N <  1000 : cn = category_name + '_%03d'  % i
        elif N < 10000 : cn = category_name + '_%04d'  % i
        else           : cn = category_name + '_%d'    % i
        category.defineType ( cn , i )
        
    ## decode inputs&weights
    
    from ostap.tools.tmva import _inputs2map_ , _weights2map_ 
    
    _inputs = _inputs2map_  ( inputs )
    
    files   = WeightsFiles  ( weights_files ).files
    files_  = [ _weights2map_ ( f ) for f in files ]

    from ostap.core.core import cpp, std, Ostap
    MAP   = std.map    ( 'std::string', 'std::string' )
    MAPS  = std.vector ( MAP ) 
    _maps = MAPS()
    for m in files_ : _maps.push_back( m ) 

    sc = Ostap.TMVA.addChoppingResponse ( dataset  ,
                                          chopper  ,
                                          category , 
                                          N        ,
                                          _inputs  ,
                                          _maps    ,
                                          prefix   ,
                                          suffix   ,
                                          aux      )
    if sc.isFailure() :
        logger.error ( 'Error from Ostap::TMVA::addChoppingResponse %s' % sc )
    return sc 

# =============================================================================
if '__main__' == __name__ :
    
    from ostap.utils.docme import docme
    docme ( __name__ , logger = logger )


# =============================================================================
# The END 
# =============================================================================
