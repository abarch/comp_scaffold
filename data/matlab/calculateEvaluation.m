function evaluation = calculateEvaluation(features)

evaluation.pitch = 14.55 * features.notesCorrect - 0.70 * features.internoteintervalstd - 10.81;
evaluation.tempo = 7.62 * features.notesCorrect - 0.68 * features.durationmean - 0.14 * features.internoteintervalstd - 1.96 * features.relativepresstimemean - 5.54; 
evaluation.rhythm = 6.75 * features.notesCorrect - 0.74 * features.durationmean - 1.62 * features.relativepresstimemean - 4.47;
evaluation.articulationDynamics = +5.43 * features.notesCorrect - 0.37 * features.durationmean - 0.16 * features.internoteintervalstd - 2.67;
evaluation.overall = 21.71 * features.notesCorrect - 1.11 * features.durationmean - 0.47 * features.internoteintervalstd - 3.19 * features.relativepresstimemean - 15.70;