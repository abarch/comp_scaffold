% READDATA -read the data from the h5 file
function results = readdata(filename)

%import pandas.*;

data = py.pandas.read_hdf(filename);
columnsPy = data.columns.tolist();
for k=1:columnsPy.length
    column{k} = char(columnsPy{k});
end

pyList = data.values.tolist();
for k=1:pyList.length
    for m=1:numel(column)
        if isa(pyList{k}{m},'double')
            results.(column{m})(k) = double(pyList{k}{m});
        else
            results.(column{m}){k} = char(pyList{k}{m});
        end
    end
end


% Did not use this way in the end
if 0
    items = h5read(filename,'/data/block0_items');
    vals = h5read(filename,'/data/block0_values');

    items = removetrailingspaces(items);

    for k=1:numel(items)
        data.(items{k}) = vals(k,:);
    end

    items = h5read(filename,'/data/block1_items');
    vals = h5read(filename,'/data/block1_values');
end