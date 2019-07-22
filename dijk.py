import networkx as nx

num_attr = 2

# Lets say we're trying to max distance and min roughness.
# This would be a long and smooth ride.
def multi_label(G, s, e):
    unvisited = list(G.nodes)
    # There is an array of previous nodes for each node,
    # given that there's more than one possible way.
    # prevnodes = {}
    labels = {k: [0, float('inf')] * num_attr for k in list(G.nodes)}

    labels[s].append([0, 0, ])

    while len(unvisited) > 0:
        unvisdist = {k: labels[k] for k in unvisited}

        # Select the unvisited node with the smallest distance,
        # it's current node now.
        current = unvisited[0]
        for k, v in unvisdist.items():
            if labels[current] > v:
                current = k

        # Find neighbours of current that are unvisited
        # and update their labels
        for neighbor, val in G[current].items():
            if neighbor in unvisited:
                # Compare the newly calculated label to the assigned
                # ones and save the dominant one.
                if labels[neighbor]['distance'] < (labels[current]['distance'] + val['distance']):
                    labels[neighbor]['distance'] = labels[current]['distance'] + val['distance']
                    # prevnodes[neighbor] = current

        unvisited.remove(current)

        # Stop, if the smallest distance among the unvisited
        # nodes is infinity.
        if current == e or labels[current] == float('inf'):
            break

    path = list()
    current = e
    while current is not None:
        path.insert(0, current)
        current = prevnodes.get(current)

    return path

def dijkstra(G, s, e, attr='weight'):
    unvisited = list(G.nodes)
    prevnodes = {}
    distance = {k: float('inf') for k in list(G.nodes)}

    distance[s] = 0

    while len(unvisited) > 0:
        unvisdist = {k: distance[k] for k in unvisited}

        # Select the unvisited node with the smallest distance,
        # it's current node now.
        current = unvisited[0]
        for k, v in unvisdist.items():
            if distance[current] > v:
                current = k

        # Find neighbours of current that are unvisited
        # and update their distances
        for neighbor, val in G[current].items():
            if neighbor in unvisited:
                # Compare the newly calculated distance to the assigned
                # and save the smaller one.
                if distance[neighbor] > (distance[current] + val[attr]):
                    distance[neighbor] = distance[current] + val[attr]
                    prevnodes[neighbor] = current

        unvisited.remove(current)

        # Stop, if the smallest distance among the unvisited
        # nodes is infinity.
        if current == e or distance[current] == float('inf'):
            break

    path = list()
    current = e
    while current is not None:
        path.insert(0, current)
        current = prevnodes.get(current)

    return path

G = nx.DiGraph()

G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K'])
G.add_edge('A', 'B', distance=5, roughness=2)
G.add_edge('A', 'H', distance=10, roughness=3)
G.add_edge('A', 'D', distance=10, roughness=4)
G.add_edge('B', 'F', distance=5, roughness=2)
G.add_edge('C', 'D', distance=5, roughness=1)
G.add_edge('D', 'G', distance=10, roughness=8)
G.add_edge('D', 'E', distance=5, roughness=6)
G.add_edge('E', 'A', distance=5, roughness=4)
G.add_edge('E', 'C', distance=10, roughness=5)
G.add_edge('E', 'K', distance=10, roughness=4)
G.add_edge('F', 'G', distance=15, roughness=3)
G.add_edge('G', 'C', distance=5, roughness=2)
G.add_edge('G', 'A', distance=10, roughness=1)
G.add_edge('H', 'B', distance=5, roughness=1)
G.add_edge('H', 'K', distance=20, roughness=1)
G.add_edge('K', 'B', distance=10, roughness=1)
# G.add_weighted_edges_from([('A', 'B', 5), ('A', 'H', 10),
#                            ('A', 'D', 10), ('B', 'F', 5),
#                            ('C', 'D', 5), ('D', 'G', 10),
#                            ('D', 'E', 5), ('E', 'A', 5),
#                            ('E', 'C', 10), ('E', 'K', 10),
#                            ('F', 'G', 15), ('G', 'C', 5),
#                            ('G', 'A', 10), ('H', 'B', 5),
#                            ('H', 'K', 20), ('K', 'B', 10)])

print(nx.dijkstra_path(G, 'A', 'K', 'distance'))

# print(G['A'])

print(dijkstra(G, 'A', 'K', 'distance'))
