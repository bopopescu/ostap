// ============================================================================
#ifndef OSTAP_TOPICS_H 
#define OSTAP_TOPICS_H 1
// ============================================================================
// Include files 
// ============================================================================
// STD&STL
// ============================================================================
#include <set>
#include <string>
// ============================================================================
// ROOT&RooFit 
// ============================================================================
#include "RooGlobalFunc.h"
// ============================================================================
namespace Ostap 
{
  // ==========================================================================
  namespace Utils 
  {
    // ========================================================================
    /** remove topic from the stream 
     *  @see RooMgsService 
     *  @see RooFit::MsgTopic
     *  @see RooFit::MsgLevel 
     *  @return true if topic is removed 
     */
    bool remove_topic 
    ( const unsigned short   stream                , 
      const unsigned short   topic                 ,
      const RooFit::MsgLevel level  = RooFit::INFO ) ;
    // ======================================================================
    /** add topic topic from the stream 
     *  @see RooMgsService 
     *  @see RooFit::MsgTopic
     *  @return true if topic is added 
     */
    bool add_topic 
    ( const unsigned short stream , 
      const unsigned short topic  ) ;
    // ========================================================================
    class RemoveTopic 
    {
    public:
      // ======================================================================
      RemoveTopic ( const unsigned short   topics                 , 
                    const RooFit::MsgLevel level   = RooFit::INFO ,
                    const int              stream  =  -1          ) ;
      // ======================================================================
      /// destructor 
      ~RemoveTopic () ;
      // ======================================================================
    public:
      // ======================================================================
      void exit() ;
      // ======================================================================
    private :
      // ======================================================================
      unsigned short           m_topics   { 0 }            ;
      RooFit::MsgLevel         m_level    { RooFit::INFO } ;
      std::set<unsigned short> m_streams  {   }            ;
      // ======================================================================
    };
    // ========================================================================
    class AddTopic 
    {
    public:
      // ======================================================================
      AddTopic ( const unsigned short   topics                 , 
                 const int              stream  =  -1          ) ;
      // ======================================================================
      /// destructor 
      ~AddTopic () ;
      // ======================================================================
    public:
      // ======================================================================
      void exit() ;
      // ======================================================================
    private :
      // ======================================================================
      unsigned short           m_topics   { 0 }            ;
      RooFit::MsgLevel         m_level    { RooFit::INFO } ;
      std::set<unsigned short> m_streams  {   }            ;
      // ======================================================================
    };
    // ========================================================================

    // ========================================================================
  } //                                       The end  of namespace Ostap::Utils 
  // ==========================================================================
} //                                                 The end of namespace Ostap
// ============================================================================
//                                                                      The END 
// ============================================================================
#endif // OSTAP_TOPICS_H
// ============================================================================