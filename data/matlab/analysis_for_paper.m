% Analysis for paper

data1 = readdata('data_expert_demo.h5');
data2 = readdata('data_expert_demo2.h5');
combined = combine(data1,data2);

w = 0:0.05:1;
for k=1:numel(w)
    [results(k),selected(k,:),factorNames] = doLinearRegression(combined,'combined',w(k),0);
end

% CALCULATE THE ACCURACY AND PICK THE BEST ONE

% 0 = timing, 1 = pitch
groundtruth = strcmp(combined.practice_mode,'IMP_PITCH');

% calculate the difference

errors = sum(abs(selected - groundtruth),2);
