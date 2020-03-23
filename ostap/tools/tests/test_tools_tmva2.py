#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
## @file ostap/tools/tests/test_tools_tmva.py
#
#  Test for TMVA machinery
# 
#  @author Vanya BELYAEV Ivan.Belyaev@itep.ru
#  @date 2015-10-25 
# =============================================================================
"""Test for TVMA machinery in  Ostap
"""
# =============================================================================
__version__ = "$Revision:"
__author__  = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__    = "2015-10-26"
__all__     = ()  ## nothing to be imported 
# =============================================================================
import ROOT, os
import ostap.io.root_file 
from   builtins                 import range
from   ostap.core.core          import ROOTCWD
from   ostap.utils.progress_bar import progress_bar 
from   array                    import array
# =============================================================================
# logging 
# =============================================================================
from ostap.logger.logger import getLogger
if '__main__' == __name__  or '__builtin__'  == __name__ : 
    logger = getLogger ( 'ostap.test_tools_tmva2' )
else : 
    logger = getLogger ( __name__ )
# ==============================================================================
from ostap.utils.cleanup import CleanUp
data_file = CleanUp.tempfile ( suffix = '.root' , prefix = 'test_tools_tmva2_' )
if not os.path.exists( data_file ) :
    import random 
    nB = 10000
    nS = 10000
    logger.info('Prepare input ROOT file with data  %s' % data_file )
    with ROOT.TFile.Open( data_file ,'recreate') as test_file:
        ## test_file.cd()
        treeSignal = ROOT.TTree('S','signal     tree')
        treeBkg    = ROOT.TTree('B','background tree')
        treeSignal.SetDirectory ( test_file ) 
        treeBkg   .SetDirectory ( test_file ) 
        
        from array import array 
        var1 = array ( 'd', [0] )
        var2 = array ( 'd', [0] )
        var3 = array ( 'd', [0] )
        
        treeSignal.Branch ( 'var1' , var1 , 'var1/D' )
        treeSignal.Branch ( 'var2' , var2 , 'var2/D' )
        treeSignal.Branch ( 'var3' , var3 , 'var3/D' )
        
        treeBkg   .Branch ( 'var1' , var1 , 'var1/D' )
        treeBkg   .Branch ( 'var2' , var2 , 'var2/D' )
        treeBkg   .Branch ( 'var3' , var3 , 'var3/D' )
        
        ## fill background tuple: 
        #for i in progress_bar ( range ( nB ) ) : 
        for i in range ( nB ) : 
            
            x = random.uniform ( -2.0 , 2.0 )
            y = random.uniform ( -2.0 , 2.0 )
            z = random.gauss   (   .0 , 0.5 )
            
            var1[0] =  x + 0.1 * y  
            var2[0] =  x - 0.1 * y  
            var3[0] = -x +       z
            
            treeBkg.Fill()
            
        ## fill signal tuple: 
        #for i in progress_bar ( range ( nS ) ) : 
        for i in range ( nS ) : 
            
            x = random.gauss  (  0.0 , 0.1 )
            y = random.gauss  (  0.0 , 0.2 )
            z = random.gauss  (  0.5 , 0.5 )
            
            var1[0] =  x
            var2[0] =  y  
            var3[0] =  z 
            treeSignal.Fill()
            
        test_file.Write()
        test_file.ls()

        
logger.info('Create and train TMVA')
with ROOT.TFile.Open( data_file ,'READ') as datafile : 
    datafile.ls()
    tSignal  = datafile['S']
    tBkg     = datafile['B']
    
    #
    ## book TMVA trainer
    #
    from ostap.tools.tmva import Trainer 
    trainer = Trainer (
        name    = 'TestTMVA2' ,   
        methods = [ # type               name   configuration
        ( ROOT.TMVA.Types.kMLP        , "MLP"         , "H:!V:EstimatorType=CE:VarTransform=N:NCycles=200:HiddenLayers=N+3:TestRate=5:!UseRegulator" ) ,
        ( ROOT.TMVA.Types.kBDT        , "BDTG"        , "H:!V:NTrees=1000:MinNodeSize=2.5%:BoostType=Grad:Shrinkage=0.10:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=100:MaxDepth=2" ) , 
        ## ( ROOT.TMVA.Types.kBDT        , "BDTB"        , "H:!V:NTrees=1000:BoostType=Bagging:SeparationType=GiniIndex:nCuts=20" )  , 
        ## ( ROOT.TMVA.Types.kBDT        , "BDTD"        , "H:!V:NTrees=1000:MinNodeSize=5%:MaxDepth=3:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=20:VarTransform=Decorrelate" ) ,        
        ( ROOT.TMVA.Types.kCuts       , "Cuts"        , "H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart" ) ,
        ( ROOT.TMVA.Types.kFisher     , "Fisher"      , "H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" ),
        ## ( ROOT.TMVA.Types.kFisher     , "FisherG"     , "H:!V:VarTransform=Gauss"  ),
        ## ( ROOT.TMVA.Types.kFisher     , "FisherB"     , "H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2:!Boost_DetailedMonitoring" ),
        ## ( ROOT.TMVA.Types.kSVM        , "SVM"         , "H:!V:Gamma=0.25:Tol=0.001:VarTransform=Norm" ) ,
        ( ROOT.TMVA.Types.kLikelihood , "Likelihood"  , "H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50" ) ,
        ## ( ROOT.TMVA.Types.kLikelihood , "LikelihoodD" , "H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate" ), 
        ## ( ROOT.TMVA.Types.kHMatrix    , "HMatrix"     , "H:!V:VarTransform=None" ) ,
        ## ( ROOT.TMVA.Types.kRuleFit    , "RuleFit"     , "H:!V:RuleFitModule=RFTMVA:Model=ModRuleLinear:MinImp=0.001:RuleMinDist=0.001:NTrees=20:fEventsMin=0.01:fEventsMax=0.5:GDTau=-1.0:GDTauPrec=0.01:GDStep=0.01:GDNSteps=10000:GDErrScale=1.02" ),
        ## ( ROOT.TMVA.Types.kPDERS      , "PDERS"       , "H:!V:NormTree=T:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600" ) ,
        ## ( ROOT.TMVA.Types.kKNN        , "KNN"         , "H:!V:nkNN=20:ScaleFrac=0.8:SigmaFact=1.0:Kernel=Gaus:UseKernel=F:UseWeight=T:!Trim" ) ,
        ] ,
        variables = [ 'var1' , 'var2' ,  'var3' ] , ## Variables for training 
        signal         = tSignal                  , ## ``Signal'' sample
        background     = tBkg                     , ## ``Background'' sample         
        verbose        = True  )
    
    from ostap.utils.timing import timing
    with timing ( 'for TMVA training' , logger ) : 
        weights_files = trainer.train ()
        tar_file      = trainer.tar_file

# =============================================================================
if os.path.exists ( trainer.output_file ) :
    os.remove ( trainer.output_file )

# =============================================================================
## Use trained TMVA
#  There are two alternatives
#  - usage of TMVA Reader : it can be  rather slow,
#    but it is very flexible and powerful with respect to variable transformations
#  - addTMVAResponse function : it is less flexible, but very CPU efficient 
# =============================================================================

## prepare dataset with TMVA result

from ostap.fitting.selectors import SelectorWithVars, Variable     
## 1) Book RooDataset                 
variables = [
    Variable( 'var1' , 'variable#1' ) ,
    Variable( 'var2' , 'variable#2' ) ,
    Variable( 'var3' , 'variable#3' ) ,
    ]

## 2) create TMVA reader
from ostap.tools.tmva import Reader
reader = Reader( 'MyMLP' ,
                 variables     = [ ('var1' , lambda s : s.var1 )   ,
                                   ('var2' , lambda s : s.var2 )   ,
                                   ('var3' , lambda s : s.var3 ) ] ,
                 weights_files = tar_file   )

methods = reader.methods[:]

## # =============================================================================
## ## A: Use TMVA  reader
## #  - It can be slow, but it allows on-flight varibales transformation
## #  - much more efficient alternativeis <code>addTMVAResponse</code> function
## # =============================================================================

## # =============================================================================
## ## 2.1) few trivial tests: use the methods/reader as simple function
## for m in methods :
##     method = reader[m]
##     logger.info ( 'Method  %12s , response %s' % ( m , method ( 1.1 , 0.8 , 0.3 ) ) )
##     del method 
## # =============================================================================

## ## 2.2) declare/add TMVA  variables with TMVAreader 
## for m in methods :
##     variables += [ Variable( 'tmva_%s' % m , 'TMVA(%s)' % m , accessor = reader[m] ) ]
## # =============================================================================
## ## The END of TMVA.Reader fragment 
## # =============================================================================


# =============================================================================
## read input data file 
with ROOT.TFile.Open( data_file ,'READ') as datafile :
    
    datafile.ls()
    tSignal  = datafile['S']
    tBkg     = datafile['B']

    # =========================================================================
    ## B: addTMVAResponse
    #  Much better alternative to TMVA.Reader:
    #  - it has much better performance  :-) 
    #  - but it is less flexible with  repsect to varibale  transformation :-(
    # =========================================================================
    
    from ostap.tools.tmva import addTMVAResponse
    addTMVAResponse ( tSignal ,
                      inputs        = ( 'var1' ,  'var2' , 'var3' ) ,
                      weights_files = tar_file ,
                      prefix        = 'tmva_'     ,
                      suffix        = '_response' )
    addTMVAResponse ( tBkg    ,
                      inputs        = ( 'var1' ,  'var2' , 'var3' ) ,
                      weights_files = tar_file ,
                      prefix        = 'tmva_'     ,
                      suffix        = '_response' )
    
    # =========================================================================
    ## The END of addTMVAResponse  fragment
    # =========================================================================

# =============================================================================
## read input data file 
with ROOT.TFile.Open( data_file ,'READ') as datafile :
    
    datafile.ls()
    tSignal  = datafile['S']
    tBkg     = datafile['B']

    logger.info ('tree SIG:\n%s' %  tSignal )
    logger.info ('tree BKG:\n%s' %  tBkg    )
    
    for m in methods :
        
        ms = tSignal.statVar('tmva_%s_response' % m )
        mb = tBkg   .statVar('tmva_%s_response' % m )
        
        logger.info('TMVA:%-11s for signal&background: %+.2f+-%.2f(S) vs %+.2f+-%.2f(B)' % ( m, ms.mean().value() , ms.rms() , mb.mean().value() , mb.rms() ) )
        

# =============================================================================
# The END
# =============================================================================    
