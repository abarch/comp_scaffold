% initial_analysis2 - 2nd try

data1 = readdata('data_expert_demo.h5');
data2 = readdata('data_expert_demo2.h5');
combined = combine(data1,data2);

%% look at correlations
figure;
combined_matrix = [combined.error_before_right_timing' combined.error_before_right_pitch' combined.error_after_right_timing' combined.error_after_right_pitch'];
[~,h] = plotmatrix(combined_matrix);
ylabel(h(1,1),'Error before timing');
ylabel(h(2,1),'Error before pitch');
ylabel(h(3,1),'Error after timing');
ylabel(h(4,1),'Error after pitch');

xlabel(h(4,1),'Error before timing');
xlabel(h(4,2),'Error before pitch');
xlabel(h(4,3),'Error after timing');
xlabel(h(4,4),'Error after pitch');


%%
groundtruth = strcmp(combined.practice_mode,'IMP_PITCH');

X = [ones(size(combined.error_before_right_pitch')) combined.error_before_right_pitch' combined.error_before_right_timing' groundtruth'];
X_pitchtraining = X;
X_pitchtraining(:,4) = 1;

X_timingtraining = X;
X_timingtraining(:,4) = 0;

MEAN_UTILITY = 0.75;

as = 0:0.01:1;

for n = 1:numel(as)
    a = as(n);

    utility = - a * (combined.error_after_right_pitch - combined.error_before_right_pitch)' ...
        - (1-a) * (combined.error_after_right_timing - combined.error_before_right_timing)' - MEAN_UTILITY;

    Y = utility;
    [b,~,~,~,stats] = regress(utility,X);
    Rsquared(n) = stats(1);
    F(n) = stats(2);
    p(n) = stats(3);

    utility_predicted_pitchtraining(n,:)  = b' * X_pitchtraining';
    utility_predicted_timingtraining(n,:) = b' * X_timingtraining';
end

predicted_practice = utility_predicted_pitchtraining > utility_predicted_timingtraining;

accuracy = mean(predicted_practice == groundtruth,2);

utility_predicted = b' * X';

%%
% So this is using a = 1
figure;
plot(utility(groundtruth==0),utility_predicted(groundtruth==0),'.','MarkerSize',15);
hold on;
plot(utility(groundtruth==1),utility_predicted(groundtruth==1),'.','MarkerSize',15);
plot([-1 0],[-1 0],'k--')
axis equal;
xlabel('Actual utility');
ylabel('Predicted utility');
legend('Timing training','Pitch training','Location','NorthWest')
set(gca,'Box','off');
set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 10 10]);
print('-depsc2','figures/actual_predicted_utility')

