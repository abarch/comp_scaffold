% COMBINE - combine two data sets

function combined = combine(first,second)

f = fields(first);

for k=1:numel(f)
    combined.(f{k}) = [first.(f{k}) second.(f{k})];
end