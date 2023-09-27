%%%%%% NOT COMPLETED %%%%%%%%

% At the moment, there is just 1 hyperparameter - the weight 
% utility = - (diff_timing*weight + diff_pitch*(1-weight)) - MEAN_UTILITY;

function optimizeHyperparameters(data)

% expert label
% double check the practice modes are as we expect
if ~all(strcmp(data.practice_mode,'IMP_TIMING') + strcmp(data.practice_mode,'IMP_PITCH'))
    error('some of the trials have practice modes that are not TIMING or PITCH');
end

% 1 = PITCH, 0 = TIMING
practicemodes = strcmp(data.practice_mode,'IMP_PITCH');

factors = [data.bpm' data.error_before_right_timing' data.error_before_right_pitch'];

%`utility = calculateUtility(data,weight);

tokeep = max(factors) > min(factors);
factors = factors(:,tokeep);
factorNums = 1:4;
numsUsed = factorNums(tokeep);
allnames = {'BPM','errorbefore_timing','errorbefore_pitch'};
selectednames = allnames(tokeep)

outcome1 = data.error_after_right_timing';
outcome2 = data.error_after_right_pitch';

% we can use logistic regression to find the best fit parameters including
% the hyperparameter
[logitCoef] = glmfit(factors,practicemodes','binomial','logit')
