// ============================================================================
#ifndef OSTAP_DATAFRAME_H 
#define OSTAP_DATAFRAME_H 1
// ============================================================================
// Include files
// ============================================================================
// ROOT
// ============================================================================
#include "RVersion.h" // ROOT 
// ============================================================================
// ROOT::ROOT
// ============================================================================
/** @file Ostap/DataFrame.h
 *  the   first attemps to use ROOT (R,T)DataFrame
 */
// ============================================================================
#if ROOT_VERSION_CODE >= ROOT_VERSION(6,14,0)
namespace ROOT  { class         RDataFrame           ; }
namespace Ostap { 
  /** @typename DataFrame 
   *  the actual type of data-frame
   *  @see ROOT::RDataFrame 
   */
  typedef ROOT::RDataFrame DataFrame ;
}
#else 
namespace ROOT  { namespace Experimental { class TDataFrame ; } }
namespace Ostap { 
  // ==========================================================================
  /** @typename DataFrame 
   *  the actual type of data-frame
   *  @see ROOT::Experimental::TDataFrame; 
   */
  typedef ROOT::Experimental::TDataFrame DataFrame ; 
  // ==========================================================================
}
#endif 
// ============================================================================
#endif // OSTAP_DATAFRAME_H
// ============================================================================
