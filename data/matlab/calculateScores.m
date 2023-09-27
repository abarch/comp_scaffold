% calculateScores
%
% details is an .xlsx file with the columns 
% xmlfilename	BPM	pre	post
% xmlfile - which file
% pre  - which trial this is the pretest for
% post - which trial this is the posttest for 
%
% dirname is where to find the xml files

function [scores,features] = calculateScores(details,dirname)

t = readtable(details);

removeMetronome = 1;

for k=1:size(t,1)
    fn = t.xmlfilename{k};
    [target,played] = readxmlfile([dirname '/' fn],removeMetronome);
    idealoverallduration = 10;
    features(k) = calculateFeatures(played,target,idealoverallduration);
    scores(k) = calculateEvaluation(features(k));
end

% turn into tables
features = struct2table(features);
scores = struct2table(scores);