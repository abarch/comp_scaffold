% INITIAL_ANALYSIS

data1 = readdata('data_expert_demo.h5');
data2 = readdata('data_expert_demo2.h5');
combined = combine(data1,data2);

doLinearRegression(data1,'firstexperiment',0.5);
doLinearRegression(data2,'secondexperiment',0.5);
results = doLinearRegression(combined,'combined',0.5);

% Find the optimal weight

b_timingerror = results.mdl_timingerror.Coefficients.Estimate;
b_pitcherror = results.mdl_pitcherror.Coefficients.Estimate;

% 0 = timing, 1 = pitch for the second column (third column after
% including a column of 1s for the intercept)
X = [ones(size(results.factors,1),1) results.factors];
X_timingpractice = X;
X_timingpractice(:,3) = 0;
X_pitchpractice = X;
X_pitchpractice(:,3) = 1;

timingerror_timingpractice = b_timingerror' * X_timingpractice';
timingerror_pitchpractice  = b_timingerror' * X_pitchpractice';

pitcherror_timingpractice = b_pitcherror' * X_timingpractice';
pitcherror_pitchpractice  = b_pitcherror' * X_pitchpractice';

% 0 = timing, 1 = pitch
groundtruth = strcmp(combined.practice_mode,'IMP_PITCH');

% test - graph it
xs = 0:0.01:1;
for k=1:numel(xs)
    r(k) = costFunction(xs(k),groundtruth,timingerror_timingpractice,timingerror_pitchpractice,pitcherror_timingpractice,pitcherror_pitchpractice,combined);
end
figure;
% weight * timing error + (1-weight)* pitch error
plot(xs,r);
xlabel('Weight (0=only pitch, 1=only timing)');
ylabel('Mismatch probability');

% optimal value for the weight is anything between 0 and ~0.7 Why so sudden
% a jump? because the errors are linearly related

figure;plot(timingerror_pitchpractice,timingerror_timingpractice,'r*')
hold on;plot(pitcherror_pitchpractice,pitcherror_timingpractice,'b*');
xlabel('Predicted pitch practice error after'); ylabel('Predicted timing practice error after');
legend('Timing error','Pitch error');

% Does not work - probably because it is not continuous
% starting guess
x0 = 0.8;
result = fminsearch(@(weight) costFunction(weight,groundtruth,timingerror_timingpractice,timingerror_pitchpractice,pitcherror_timingpractice,pitcherror_pitchpractice,combined),x0)

