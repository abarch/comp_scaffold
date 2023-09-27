% PLOTDATA - plot data from an h5 file
function h = plotdata(filename,tosave)

if nargin<2
    tosave = 0;
end

if isstruct(filename)
    data = filename;
else
    data = readdata(filename);
end

colors = colororder;

% just RH for now
numtrials = numel(data.error_before_right_timing);
x1 = (1:numtrials)-0.2;
x2 = (1:numtrials)+0.2;

figure;
for n=1:numtrials
    h(1) = plot([x1(n) x2(n)],...
        [data.error_before_right_timing(n) data.error_after_right_timing(n)],...
        'Color',colors(1,:));
    hold on;
    h(2) = plot([x1(n) x2(n)],...
        [data.error_before_right_pitch(n) data.error_after_right_pitch(n)],...
        'Color',colors(2,:));
end

utility = calculateUtility(data,0.5);
% Plot the utility also

h(3) = plot(1:numtrials,utility,'go');

% add in the practice modes
yl = ylim;
alpha = 0.1;
for n=1:numtrials
    if strcmp(data.practice_mode{n},'IMP_TIMING')
        pm = 1;
    else
        pm = 2;
    end
    area([n-0.1 n+0.1],[yl(2) yl(2)],'FaceColor',colors(pm,:),'EdgeColor',colors(pm,:),'FaceAlpha',alpha,'EdgeAlpha',alpha);
end

legend(h,'timing error','pitch error','utility','Location','NorthEast')
ylabel('Error / Utility');
% add in the names of the songs
set(gca,'XTick',1:numtrials,'XTickLabel',strrep(data.midi_filename,'_',' '));

if tosave
    set(gcf,'PaperUnits','centimeters','PaperPosition',[0 0 40 10]);
    print('-dpng',['figures/' filename(1:end-3)]);
end
