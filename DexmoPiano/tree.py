from task_generation.generator import TaskParameters
from task_generation.note_range_per_hand import NoteRangePerHand




# add root



# def next_level(index):
#     highest = 1
#
#     n=G.nodes[index]
#
#     for  key,value in  n.items():
#         print (key,value)
#         if key == "note_range_right":
#             G.add_node(highest, note_range_left = value+1, rhythm_res_left=n['rhythm_res_left'],
#                        note_range_right=n['note_res_right'], rhythm_res_right=n['note_res_right'])
#             G.add_edge(index, highest)
#             highest += 1

# next_level(0)
def exp_graph(dim=(2,3,4)):
    import networkx as nx
    G = nx.grid_graph(dim)
    #G= nx.grid_graph(dim=(2,3,4,5))
    for line in nx.generate_adjlist(G):
        print(line)

    print (G.nodes())
    import matplotlib.pyplot as plt
    # nx.spring_layout

    nx.draw(G)
    plt.draw()
    plt.show()



import plotly.graph_objects as go
import networkx as nx

G= nx.grid_graph(dim=(2,3,4,5))

Num_nodes = len(G.nodes)

# plt.figure(figsize=(5,5))
edges = G.edges()

# ## update to 3d dimension
spring_3D = nx.spring_layout(G, dim = 3, k = 0.5) # k regulates the distance between nodes
# weights = [G[u][v]['weight'] for u,v in edges]
# nx.draw(G, with_labels=True, node_color='skyblue', font_weight='bold',  width=weights, pos=pos)

# we need to seperate the X,Y,Z coordinates for Plotly
# NOTE: spring_3D is a dictionary where the keys are 1,...,6
x_nodes= [spring_3D[key][0] for key in spring_3D.keys()] # x-coordinates of nodes
y_nodes = [spring_3D[key][1] for key in spring_3D.keys()] # y-coordinates
z_nodes = [spring_3D[key][2] for key in spring_3D.keys()] # z-coordinates

#we need to create lists that contain the starting and ending coordinates of each edge.
x_edges=[]
y_edges=[]
z_edges=[]

#create lists holding midpoints that we will use to anchor text
xtp = []
ytp = []
ztp = []

#need to fill these with all of the coordinates
for edge in edges:
    #format: [beginning,ending,None]
    x_coords = [spring_3D[edge[0]][0],spring_3D[edge[1]][0],None]
    x_edges += x_coords
    xtp.append(0.5*(spring_3D[edge[0]][0]+ spring_3D[edge[1]][0]))

    y_coords = [spring_3D[edge[0]][1],spring_3D[edge[1]][1],None]
    y_edges += y_coords
    ytp.append(0.5*(spring_3D[edge[0]][1]+ spring_3D[edge[1]][1]))

    z_coords = [spring_3D[edge[0]][2],spring_3D[edge[1]][2],None]
    z_edges += z_coords
    ztp.append(0.5*(spring_3D[edge[0]][2]+ spring_3D[edge[1]][2]))


#etext = [f'weight={w}' for w in edge_weights]

# trace_weights = go.Scatter3d(x=xtp, y=ytp, z=ztp,
#     mode='markers',
#     marker =dict(color='rgb(125,125,125)', size=1), #set the same color as for the edge lines
#     text = etext, hoverinfo='text')

#create a trace for the edges
trace_edges = go.Scatter3d(
    x=x_edges,
    y=y_edges,
    z=z_edges,
    mode='lines',
    line=dict(color='black', width=2),
    hoverinfo='none')

#create a trace for the nodes
trace_nodes = go.Scatter3d(
    x=x_nodes,
    y=y_nodes,
    z=z_nodes,
    mode='markers',
    marker=dict(symbol='circle',
            size=10,
            color='skyblue')
    )

#Include the traces we want to plot and create a figure
data = [trace_edges, trace_nodes] #, trace_weights]
fig = go.Figure(data=data)

fig.show()