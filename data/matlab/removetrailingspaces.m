function itemsCleaned = removetrailingspaces(items)

if isa(items,'string') && numel(items)>1
    for k=1:numel(items)
        itemsCleaned(k) = removetrailingspaces(items(k));
    end
    return
end

for k=1:numel(items)
    itemsChar = char(items);
    lastnonspace = find(itemsChar~=0,1,'last');
    itemsCleaned = string(itemsChar(1:lastnonspace));
end