% This is supposed to return a structure similar to that of readmidifile
%
%
% data = readmidifile(fn)
% fn is the filename
% data is a struct with 5 fields:
% data.note are the notes played 
% data.onset are the onset times (in seconds)
% data.duration are the note durations (in seconds) - time from press to
%                                                     release
% data.pressvelocity is the velocity when presed
% data.releasevelocity is the release velocity

% The metronome is coded as the left hand in some of these pieces 
% midicodes - (39 42 42 42), if removeMetronome is included
% then remove these notes

function [target,played] = readxmlfile(fn,removeMetronome,childnumber)

if nargin<2
    removeMetronome = 0;
end

if nargin<3
    childnumber = [];
end

x = parseXML(fn);

if ~strcmp(x.Children(1).Name,'target_notes')
    error('First child in xml file should be target_notes');
end

if ~strcmp(x.Children(1).Children(1).Name,'notes')
    error('First child of first child should be notes');
end

target = parsenotes(x.Children(1).Children(1).Children.Data,removeMetronome);

if ~strcmp(x.Children(2).Name,'trials')
    error('Second child should be trials');
end

numchildren = numel(x.Children(2).Children);

if numchildren>1 && isempty(childnumber)
    error('There are more than 1 child - need to specify child number as third argument');
end

if childnumber > numchildren
    error(['There are ' num2str(numchildren) ' so cannot calculate for child ' num2str(childnumber)]);
end

if numchildren==1
    childnumber = 1;
end

if ~strcmp(x.Children(2).Children(childnumber).Name,'trial')
    error('Child of second child should be trial');
end

if ~strcmp(x.Children(2).Children(childnumber).Children(1).Name,'notes')
    error('First child of first child of second child should be notes');
end

played = parsenotes(x.Children(2).Children(childnumber).Children(1).Children(1).Data,0);


function notes = parsenotes(data,removeMetronome)

starts = strfind(data,'{');
ends = strfind(data,'}');

count = 0;
notes.note = [];
notes.onset = [];
notes.duration = [];
notes.pressvelocity = [];
notes.releasevelocity = [];

for k=1:numel(starts)
    thisdata = data(starts(k):ends(k));
    t = regexp(thisdata,'{"pitch": ([0-9]*), "velocity": ([0-9]*), "note_on_time": ([0-9\.]*), "note_off_time": ([0-9\.]*)}','tokens');
    thisnote = str2double(t{1}{1});
    thisonset = str2double(t{1}{3});
    thisoffset = str2double(t{1}{4});
    thisvelocity = str2double(t{1}{2});

    if ~removeMetronome || ~any(thisnote==[39 42])
        count = count+1;
        notes.note(count) = thisnote;
        notes.onset(count) = thisonset;
        notes.duration(count) = thisoffset - thisonset;
        notes.pressvelocity(count) = thisvelocity;
        notes.releasevelocity(count) = thisvelocity;
    end
end
