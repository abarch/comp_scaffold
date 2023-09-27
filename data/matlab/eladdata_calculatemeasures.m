% ELADDATA_calculatemeasures

detailsfns = {'2023_01_05.xlsx','2023_01_29.xlsx','2023_05_14.xlsx'};
dirnames = {'2023_01_05','2023_01_29','2023_05_14'};
datafns = {'data_expert_demo.h5','data_expert_demo2.h5','data_expert_demo3.h5'};

t_combined = table;
for f=1:numel(detailsfns)
    data = readdata(datafns{f});

    details = readtable(detailsfns{f});

    [scores,features] = calculateScores(detailsfns{f},dirnames{f});
    numitems = max(details.pre);

    scoresVariables = scores.Properties.VariableNames;
    featuresVariables = features.Properties.VariableNames;
    t = table;
    t.midi_filename = data.midi_filename';
    t.bpm = data.bpm';
    t.username = data.username';
    t.practice_mode = data.practice_mode';
    t.error_before_right_timing = data.error_before_right_timing';
    t.error_after_right_timing = data.error_after_right_timing';
    t.error_before_right_pitch = data.error_before_right_pitch';
    t.error_after_right_pitch = data.error_after_right_pitch';
    for k=1:numitems
        pre_index = find(details.pre==k);
        post_index = find(details.post==k);
        for m=1:numel(featuresVariables)
            t.(['pre_' featuresVariables{m}])(k) = features.(featuresVariables{m})(pre_index);
            t.(['post_' featuresVariables{m}])(k) = features.(featuresVariables{m})(post_index);
        end
        for m=1:numel(scoresVariables)
            t.(['pre_' scoresVariables{m}])(k) = scores.(scoresVariables{m})(pre_index);
            t.(['post_' scoresVariables{m}])(k) = scores.(scoresVariables{m})(post_index);
        end
    end
    t_combined = [t_combined;t];
end

writetable(t_combined,'combined.csv');

combined = py.pandas.read_csv('combined.csv');
combined.to_hdf('combined.h5', key='data', mode='w');
