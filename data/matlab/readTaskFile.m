% READTASKFILE

function r = readTaskFile(fn)

pickle = py.importlib.import_module('pickle');
fh = py.open(fn, 'rb');
P = pickle.load(fh);    % pickle file loaded to Python variable
fh.close();

r.practice_mode = string(P{1}.practice_mode);
r.bpm = P{1}.bpm + 0;
% There are more than can be extracted
r.noOfBars = P{2}.noOfBars + 0;

