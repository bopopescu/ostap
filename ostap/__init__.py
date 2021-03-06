#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
# Copyright Ostap developers
# =============================================================================
#                                   1.4.9.1 (Jun 01, 2020, 12:23 [UTC])
#     .oooooo.                .                        
#    d8P'  `Y8b             .o8                        
#   888      888  .oooo.o .o888oo  .oooo.   oo.ooooo.  
#   888      888 d88(  "8   888   `P  )88b   888' `88b 
#   888      888 `"Y88b.    888    .oP"888   888   888 
#   `88b    d88' o.  )88b   888 . d8(  888   888   888 
#    `Y8bood8P'  8""888P'   "888" `Y888""8o  888bod8P' 
#                                            888       
#                                           o888o      
#                                                    
#  Simple interactive PyRoot-based analysis environment to provide access
#  to zillions useful decorators for ROOT (and not only ROOT!) objects&classes
# 
# - https://github.com/OstapHEP/ostap
# - https://ostaphep.github.io/ostap-tutorials
# - https://github.com/OstapHEP/ostap-tutorials
# 
# =============================================================================
__all__ = (
    'banner'       , ## Ostap banner 
    'version'      , ## Ostap version 
    'version_info' , ## version info as named tuple
    'build_date'   , ## Ostap build/reelase date (as string)
    'build_time'   , ## Ostap build/release time (as datetime)
    )
# =============================================================================
## the  actual version of Ostap 
__version__ = "1.4.9.1"
__date__    = "Jun 01, 2020, 12:23 [UTC]"
# =============================================================================
import datetime 
from   collections import namedtuple
# =============================================================================
version      = __version__
VersionInfo  = namedtuple("VersionInfo", ('major','minor','patch','tweak'))
version_info = VersionInfo ( 1 , 4 , 9 , 1 )
build_date   = __date__
build_time   = datetime.datetime.utcfromtimestamp ( 1591014212 )
# =============================================================================
##
import ostap.fixes.fixes
# =============================================================================
## Banner
banner = r"""
                                        1.4.9.1 (Jun 01, 2020, 12:23 [UTC])
     .oooooo.                .
    d8P'  `Y8b             .o8
   888      888  .oooo.o .o888oo  .oooo.   oo.ooooo.
   888      888 d88(  "8   888   `P  )88b   888' `88b
   888      888 `"Y88b.    888    .oP"888   888   888
   `88b    d88' o.  )88b   888 . d8(  888   888   888
    `Y8bood8P'  8""888P'   "888" `Y888""8o  888bod8P'
                                            888
                                           o888o
                                           
 - https://github.com/OstapHEP/ostap
 - https://ostaphep.github.io/ostap-tutorials
 - https://github.com/OstapHEP/ostap-tutorials
"""
   
# =============================================================================
##                                                                      The END 
# =============================================================================
