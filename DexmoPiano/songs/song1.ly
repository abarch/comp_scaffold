\version "2.20.0"
\header {
   tagline = "" % removed
 }
\score {
 {
  \relative c'{\numericTimeSignature c2 c e e c c e e g g e e c c c1 \bar "|."}
}
\layout {
  \context {
      \Score 
      proportionalNotationDuration =  #(ly:make-moment 1/5)
 }
 }
\midi {\tempo 4 = 60}
}