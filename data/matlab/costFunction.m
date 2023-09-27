% The cost function calculates the difference between the model predictions
% and the ground truth (what the teacher selected)

function cost = costFunction(weight,groundtruth,timingerror_timingpractice,timingerror_pitchpractice,pitcherror_timingpractice,pitcherror_pitchpractice,data)

diff_timing_timingpractice =  timingerror_timingpractice - data.error_before_right_timing;
diff_timing_pitchpractice =   timingerror_pitchpractice  - data.error_before_right_timing;
diff_pitch_timingpractice =   pitcherror_timingpractice  - data.error_before_right_pitch;
diff_pitch_pitchpractice =    pitcherror_pitchpractice   - data.error_before_right_pitch;

MEAN_UTILITY = 0.75;

% post error should be less than pre error, so the more negative the difference, the better
% so overall more positive is better (because of the - at the front)
utility_timingpractice = - (diff_timing_timingpractice*weight + diff_pitch_timingpractice*(1-weight)) - MEAN_UTILITY;
utility_pitchpractice = - (diff_timing_pitchpractice*weight + diff_pitch_pitchpractice*(1-weight)) - MEAN_UTILITY;

toSelect(utility_timingpractice > utility_pitchpractice) = 0;
toSelect(utility_pitchpractice > utility_timingpractice) = 1;

cost = mean(abs(toSelect - groundtruth));
