% CALCULATEFEATURES  Calculate features from the MIDI data
%
% [features,tocheck,tocheckideal,details] = calculateFeatures(midi,idealmidi,idealoverallduration)
% midi is the MIDI data (output from loadmidifile)
% idealmidi is the MIDI data of the ideal performance (also output from loadmidifile)
% idealoverallduration is the ideal duration of the song (in seconds)
%
% Returns: features - a struct with the features
%          tocheck - which notes (indices) in the performance correspond to notes in the "ideal"
%          tocheckideal - which notes (indices) in the ideal correspond to those in the performance
%          details - additional quantities calculated which may be of use
%
% If no input arguments are provided, it will calculate features for all
% songs and save them in a .mat file evaluationfeatures (as well as
% including the teacher evaluations)
function [features,tocheck,tocheckideal,details] = calculateFeatures(midi,idealmidi,idealoverallduration)

if nargin==0
    [~,M_duration] = readIdealBPMs;

    d = dir('songs/real data/*/*.midi');

    for k=1:numel(d) % 25
        fn = [d(k).folder '/' d(k).name];
        midi = readmidifile(fn);
        slashes = strfind(d(k).folder,'/');
        songname = d(k).folder(slashes(end)+1:end);
        ideal_fn = ['songs/original songs/' songname '.midi'];
        idealmidi = readmidifile(ideal_fn);
        idealduration = M_duration(songname);
        features(k) = calculateFeatures(midi,idealmidi,idealduration);
    end

    t = struct2table(features);

    % Add the teacher evaluations

    % rater (8) * performance (25) * rating(8)
    [evaluation,names] = readEvaluation;
    meanevaluation = squeeze(nanmean(evaluation(:,:,1:5)));

    % same vs different piece - take the majority (could have used column 6
    % ...)
    selected_same = sum(~isnan(squeeze(evaluation(:,:,7))));
    selected_different = sum(~isnan(squeeze(evaluation(:,:,8))));
    same = selected_same > selected_different;
    different = selected_same < selected_different;
    equal = selected_same == selected_different;
    meanevaluation(same,6) = 1; % 1 = selected same
    meanevaluation(different,6) = 2; % 2 = selected different
    meanevaluation(equal,6) = 0; % does not happen

    meanevaluation(same,7) = nanmean(evaluation(:,same,7));
    meanevaluation(different,7) = NaN;
    meanevaluation(equal,7) = NaN;

    meanevaluation(same,8) = NaN;
    meanevaluation(different,8) = nanmean(evaluation(:,different,8));
    meanevaluation(equal,8) = NaN;

    for k=1:8
        t.(names{k}) = meanevaluation(:,k);
    end

    % calculate z transforms - in the end this was useless
    % because it is a linear transformation so doesn't really change
    % anything
    fieldnames = fields(t);
    for k=1:numel(fieldnames)-3
        t_ztransformed.(fieldnames{k}) = zscore(t.(fieldnames{k}));
    end

    t_ztransformed = struct2table(t_ztransformed);

    predictornames = {'Correct pitch','Duration','Note duration (slope)','Note duration (mean)','Note duration (std)',...
    'Inter-note interval (slope)','Inter-note interval (mean)','Inter-note interval (std)',...
    'Relative press time (slope)','Relative press time (mean)','Relative press time (std)',...
    'Velocity (slope)','Velocity (mean)','Velocity (std)'};

    save evaluationfeatures t t_ztransformed predictornames

    return
end

[details.dtw,ix,iy] = dtw(midi.note,idealmidi.note);
details.editdistance = editDistance(char(midi.note),char(idealmidi.note));

overallduration = midi.onset(end) + midi.duration(end) - midi.onset(1);
% Ideal overall duration is passed as a parameter
idealmididuration = idealmidi.onset(end) + idealmidi.duration(end) - idealmidi.onset(1);

% calculate difference for each note played
%[tocheck,inds] = unique(ix,'last'); % don't look at repeated notes (which were needed for DTW to work)
%tocheckideal = iy(inds);

% the other way around
[tocheckideal,inds] = unique(iy,'last'); % don't look at repeated notes (which were needed for DTW to work)
tocheck = ix(inds);

% Proportion of notes played correctly
notes = abs(sign(idealmidi.note(tocheckideal) - midi.note(tocheck)));
if numel(notes)<numel(idealmidi.note)
    notes = [notes ones(1,numel(idealmidi.note)-numel(notes))];
end

features.notesCorrect = 1-mean(notes);

features.overalldurationdifference = (overallduration - idealoverallduration) ./ idealoverallduration;

% duration = on to off
playeddurations = midi.duration(tocheck) ./ overallduration;
idealdurations = idealmidi.duration(tocheckideal) ./ idealmididuration;
Y = (playeddurations ./ idealdurations)';

% Note duration
%features.durationdifference = median(abs(playeddurations - idealdurations) ./ idealdurations);

[features.durationslope,features.durationmean,features.durationstd,details.durationoffset] = calculateparams(Y);

% to calculate onset slope
onset = midi.onset;
onset = (onset - min(midi.onset)) / overallduration;
onsetIdeal = idealmidi.onset;
onsetIdeal = (onsetIdeal - min(idealmidi.onset)) / idealmididuration;
% We need to match the notes - so only do for those in "tocheck"
onsetDiff = onset(tocheck)-onsetIdeal(tocheckideal);
% use the last value - first value as the slope
%features.onsetslope = (onsetDiff(end) - onsetDiff(1)) ./ numel(onsetDiff);
% use regression

% remove for now, use gaps instead
%%%Y = onsetDiff';
%%%[features.onsetslope,features.onsetmean,features.onsetstd,details.onsetoffset] = calculateparams(Y);

% timing = relative time (since last press) - for the 2nd note on

% for timing, use the ideal
[tocheckideal2,inds] = unique(iy,'last');
tocheck2 = ix(inds);

idealgaps = (idealmidi.onset(tocheckideal2(2:end)) - idealmidi.onset(tocheckideal2(1:end-1))) ./ idealmididuration;
actualgaps = (midi.onset(tocheck2(2:end)) -  midi.onset(tocheck2(1:end-1))) ./ overallduration;
%features.timingdifference = median(abs(actualgaps - idealgaps) ./ idealgaps);
Y = ((actualgaps - idealgaps) ./ idealgaps)';
[features.internoteintervalslope,features.internoteintervalmean,...
    features.internoteintervalstd,details.internoteintervaloffset] = calculateparams(Y);

% relativepresstime - duration / inter-note-interval
% can't calculate it for the last note

actualarticulation = playeddurations(1:end-1) ./ actualgaps;
idealarticulation = idealdurations(1:end-1) ./ idealgaps;
Y = ((actualarticulation-idealarticulation) ./ idealarticulation)';
[features.relativepresstimeslope,features.relativepresstimemean,...
 features.relativepresstimestd,details.relativepresstimesoffset] = calculateparams(Y);

playedvelocity = midi.pressvelocity(tocheck);
idealvelocity = idealmidi.pressvelocity(tocheckideal);
Y = (playedvelocity - idealvelocity)';
%features.velocitydifference = median(Y);

[features.velocityslope, features.velocitymean, ...
    features.velocitystd,details.velocityoffset] = calculateparams(Y);



if nargout>3
    details.playeddurations = playeddurations;
    details.idealdurations = idealdurations;
    details.actualgaps = actualgaps;
    details.idealgaps = idealgaps;
    details.overallduration = overallduration;
    details.idealoverallduration = idealoverallduration;
    details.idealmididuration = idealmididuration;
    details.playedvelocity = playedvelocity;
    details.idealvelocity = idealvelocity;
end

function [slope,themean,thestd,offset] = calculateparams(Y)

X = [(1:numel(Y))' ones(size(Y))];

% If there are any illegal values (-inf or inf) remove them
goodY = ~isinf(Y) & ~isnan(Y);
Y = Y(goodY);
X = X(goodY,:);

b = regress(Y,X);
predicted = b(1) * (1:numel(Y))' + b(2);
slope = b(1);
offset = b(2);
thestd = std(Y - predicted);
themean = mean(Y);
