% DOLINEARREGRESSION - predict the improvement
%
% doLinearRegression(data,filename,weight,plotgraphs)
%
% Do it for both utility, and separate regression for the two measures
% 1 → calculate utility (defined as
% (error_after_timing - error_before_timing) + (error_after_pitch - error_before_pitch) - mean_utility
% [mean utility is currently set to 0.75] (default)
% 2 → do separate regression for error_after_timing, error_after_pitch
%
function [results,toSelect,selectednames] = doLinearRegression(data,filename,weight,plotgraphs)

if nargin<3 || isempty(weight)
    weight = 0.5;
end

if nargin<4 || isempty(plotgraphs)
    plotgraphs = 0;
end

% variables: bpm
% practice mode (0 = TIMING, 1 = PITCH)
% error_before_right_timing
% error_before_right_pitch
% page number (difficulty proxy)

% outcome - error_after_right_timing
%         - error_after_right_pitch

% double check the practice modes are as we expect
if ~all(strcmp(data.practice_mode,'IMP_TIMING') + strcmp(data.practice_mode,'IMP_PITCH'))
    error('some of the trials have practice modes that are not TIMING or PITCH');
end

%pagenumbers = cellfun(@(x) str2double(x{1}), regexp(data.midi_filename,'([1-9]*).*','tokens'));

practicemodes = strcmp(data.practice_mode,'IMP_PITCH');

factors = [data.bpm' practicemodes' data.error_before_right_timing' data.error_before_right_pitch'];

utility = calculateUtility(data,weight);

% If max == min, then there is no variation in that value so it is useless as a predictor (and causes warnings)
tokeep = max(factors) > min(factors);
factors = factors(:,tokeep);
factorNums = 1:4;
numsUsed = factorNums(tokeep);
allnames = {'BPM','practicemode','errorbefore_timing','errorbefore_pitch'};
selectednames = allnames(tokeep);

outcome_timingerror = data.error_after_right_timing';
outcome_pitcherror = data.error_after_right_pitch';

mdl_timingerror = fitlm(factors,outcome_timingerror);
mdl_pitcherror = fitlm(factors,outcome_pitcherror);
mdl_utility = fitlm(factors,utility);

% Ideally we would use lasso to determine features, but there is not enough
% data for it to work
%[B,FitInfo] = lasso(factors,outcome1,'CV',10,'PredictorNames',selectednames);

predicted_timingerror = predict(mdl_timingerror);
predicted_pitcherror = predict(mdl_pitcherror);

% calculate utility based on what was selected
predicted_utility = predict(mdl_utility);

% calculate utility for the both options
b = mdl_utility.Coefficients.Estimate;
pitch = factors; timing = factors;
toreplace = find(numsUsed==2);
pitch(:,toreplace)=1;
timing(:,toreplace)=0;
predicted_utility_pitch =  (b' * [ones(size(pitch,1),1) pitch]')';
predicted_utility_timing = (b' * [ones(size(timing,1),1) timing]')';
% Timing = 0, pitch = 1
toSelect(predicted_utility_timing > predicted_utility_pitch) = 0;
toSelect(predicted_utility_pitch > predicted_utility_timing) = 1;

%fprintf('0 = TIMING, 1 = PITCH\n');
%toSelect

if plotgraphs
    h = plotdata(data);

    h(4) = plot((1:numel(predicted_timingerror))+0.2,predicted_timingerror,'b*');
    h(5) = plot((1:numel(predicted_pitcherror))+0.2,predicted_pitcherror,'r*');
    h(6) = plot((1:numel(predicted_utility)),predicted_utility,'g*');
    legend(h,'timing error','pitch error','utility','timing after prediction','pitch after prediction','utility prediction','Location','NorthEast');

    if nargin>1 && ~isempty(filename)
        set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 40 30]);
        print('-depsc2',['figures/' filename]);
    end
end


if plotgraphs
    figure;
    subplot(1,3,1);
    plot(data.error_after_right_timing,predicted_timingerror,'.','MarkerSize',15);
    hold on;
    xlabel('Timing error after');
    ylabel('Predicted timing error after');
    axis equal;
    a = axis;
    plot(a(1:2),a(1:2),'k--');
    title(sprintf('R^2 = %.2f',mdl_timingerror.Rsquared.Ordinary));

    subplot(1,3,2);
    plot(data.error_after_right_pitch,predicted_pitcherror,'.','MarkerSize',15);
    hold on;
    xlabel('Pitch error after');
    ylabel('Predicted pitch error after');
    axis equal;
    a = axis;
    plot(a(1:2),a(1:2),'k--');
    title(sprintf('R^2 = %.2f',mdl_pitcherror.Rsquared.Ordinary));

    subplot(1,3,3);
    plot(utility,predicted_utility,'.','MarkerSize',15);
    hold on;
    xlabel('Utility');
    ylabel('Predicted utility');
    axis equal;
    a = axis;
    plot(a(1:2),a(1:2),'k--');
    title(sprintf('R^2 = %.2f',mdl_utility.Rsquared.Ordinary));

    if nargin>1 && ~isempty(filename)
        set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 40 10]);
        subplot(1,3,1); axis equal
        print('-depsc2',['figures/' filename '_Rsquared']);
    end
end

results.mdl_timingerror = mdl_timingerror;
results.mdl_pitcherror = mdl_pitcherror;
results.mdl_utility = mdl_utility;
results.factors = factors;