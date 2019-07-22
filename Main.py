import networkx as nx

ninserted = 0
nremoved = 0

class Label:
    def __init__(self, node, prevnode=None):
        self.node = node
        self.summ = {}
        self.mini = {}
        self.awsum = 0
        self.awmax = float('inf')
        self.awdif = -float('inf')
        self.awint = -float('inf')
        self.hidden = False
        self.prevnode = prevnode


def aggregate(avgs, iavgs, label):
    label.awsum = 0
    for key, val in label.summ.items():
        label.awsum += val / avgs[key]

    label.awmax = 0
    for key, val in label.mini.items():
        label.awmax += val / avgs[key]

    label.awdif = label.awsum - label.awmax

    label.awint = 0
    for key, val in label.summ.items():
        label.awint += int(val * iavgs[key])
    for key, val in label.mini.items():
        label.awint -= int(val * iavgs[key])

    # print('aggregate', label.awdif)


def better_than(la, lb):
    # print(la.prevnode, '->', la.node, ' (', la.awint, ') // ', lb.prevnode, '->', lb.node, ' (', lb.awint, ')', sep='')
    return not (la.awint < lb.awint)


def best_label(tempLabels):
    best = 0

    # print(tempLabels[0].node, '->', tempLabels[0].prevnode)

    for i in range(1, len(tempLabels)):
        if better_than(tempLabels[best], tempLabels[i]):
            best = i

    # print('Best label is', tempLabels[best].prevnode, '->', tempLabels[best].node, 'with awdif', tempLabels[best].awdif)
    return best


def dominates(la, lb):
    # For better code readability, in this function it's
    # better to have many check variables, one for each
    # case

    # 0 -> la dominates lb
    # 1 -> lb dominates la
    # 2 -> la dominates lb, but lb is to be kept
    # 3 -> lb dominates la, but la is to be kept
    # 4 -> they're equal and both are to be kept
    # 5 -> they refer to the same arc

    # First we check if the labels are equal
    # checkEq = check equality
    # checkSEq = check sum equality (it's used later)

    if la.prevnode == lb.prevnode and la.node == lb.node:
        return 5

    checkEq = 1
    checkSEq = 1
    for key in la.summ:
        if la.summ[key] != lb.summ[key]:
            checkEq = 0
            checkSEq = 0
            break

    if checkEq == 1:
        for key in la.mini:
            if la.mini[key] != lb.mini[key]:
                checkEq = 0
                break

    # checkEq=1 at this point means they're equal
    if checkEq == 1:
        # print('EQUAL')
        return 4

    # checkSLEq = check sum lower equality
    checkSLEq = 1
    for key in la.summ:
        if la.summ[key] > lb.summ[key]:
            checkSLEq = 0
            break

    # checkMGEq = check max greater equality
    checkMGEq = 1
    for key in la.mini:
        if la.mini[key] < lb.mini[key]:
            checkMGEq = 0
            break

    if checkSLEq == 1 and checkMGEq == 1:
        # This check is for finding the maximal complete set,
        # you can comment it, leaving only the 'return 0',
        # if you want only the minimal complete set
        if checkSEq == 1:
            return 3
        return 1

    # checkSGEq = check sum greater equality
    checkSGEq = 1
    for key in la.summ:
        if la.summ[key] < lb.summ[key]:
            checkSGEq = 0
            break

    # checkMLEq = check max lower equality
    checkMLEq = 1
    for key in la.mini:
        if la.mini[key] > lb.mini[key]:
            checkMLEq = 0
            break

    if checkSGEq == 1 and checkMLEq == 1:
        # Again, this is for finding the maximal complete set
        if checkSEq == 1:
            return 2
        return 0

    # print ('NO RELATION')
    return 4


def try_insert(permLabels, tempLabels, label):
    global ninserted, nremoved

    # print('Trying to insert', label.prevnode, '->', label.node)

    for perm in permLabels:
        if perm.hidden:
            # Do not check this one as there's a
            # better one in the list
            continue
        else:
            dominance = dominates(label, perm)

        if dominance == 1:
            # The new label is dominated, drop it
            # print('   It\'s dominated')
            return 0
        elif dominance == 3:
            # Accept new label as hidden
            label.hidden = True
        elif dominance == 5:
            # print("It's equal, ignore")
            return 0

    inserted = False
    rem = []
    for i in range(len(tempLabels)):
        dominance = dominates(label, tempLabels[i])

        if dominance == 0:
            # tempLabel[i] is dominated by the new label,
            # so it can be simply replaced
            if not inserted:
                # print('DOMINATES')
                tempLabels[i] = label
                # ninserted += 1
                # print('Inserted A', ninserted)
                # nremoved += 1
                # print('Removed A', nremoved)
                inserted = True
            else:
                rem.append(i)

        elif dominance == 1:
            # print('   It\'s dominated')
            # The new label is dominated
            return 0
        elif dominance == 2:
            tempLabels[i].hidden = True
            if not inserted:
                tempLabels.insert(i, label)
                # ninserted += 1
                # print('Inserted B', ninserted)
                inserted = True
        elif dominance == 3:
            label.hidden = True
            # Insert label later
        elif dominance == 4:
            if not inserted:
                if better_than(label, tempLabels[i]) == 0:
                    # ninserted += 1
                    # print('Inserted C', ninserted)
                    # print('Sum:')
                    # for k in label.summ.keys():
                    #     print('  ', label.summ[k], '<=>', tempLabels[i].summ[k])
                    # print('Minmax:')
                    # for k in label.mini.keys():
                    #     print('  ', label.mini[k], '<=>', tempLabels[i].mini[k])
                    tempLabels.insert(i, label)
                    inserted = True
        elif dominance == 5:
            # There's already a permanent label for this arc
            return 0

    if not inserted:
        tempLabels.append(label)
        # ninserted += 1
        # print('Appended', ninserted)

    removed = 0
    for i in rem:
        # nremoved += 1
        # print('Removed B', nremoved)
        del tempLabels[i - removed]
        removed += 1


def labelling(G, avgs, iavgs, permLabels, tempLabels, current):
    for neighbor, val in G[current.node].items():
        lab = Label(node=neighbor, prevnode=current.node)

        # Attributes to be summed
        for key, attr in current.summ.items():
            lab.summ[key] = attr + val[key]
            # print(attr)

        # Attributes to be minimized
        for key, attr in current.mini.items():
            lab.mini[key] = min(attr, val[key])
            # print(attr)

        aggregate(avgs, iavgs, lab)
        try_insert(permLabels, tempLabels, lab)


def mosp(G, s, sum_attr, min_attr, narcs):
    global nremoved

    avgs = {}
    iavgs = {}
    permLabels = []
    tempLabels = []

    start = Label(node=s)
    start.prevnode = s
    for i in sum_attr:
        start.summ[i] = 0
    for i in min_attr:
        start.mini[i] = float('inf')
    permLabels.append(start)

    for u, v, data in G.edges().data():
        for key, val in data.items():
            if key not in avgs:
                avgs[key] = val
            else:
                avgs[key] += val

    wmax = -float('inf')
    for k in avgs.keys():
        avgs[k] = avgs[k] / narcs
        if avgs[k] > wmax:
            wmax = avgs[k]

    # print(wmax)
    # print(avgs)

    EPS = 0.0001
    for k in avgs.keys():
        iavgs[k] = int(wmax/avgs[k] + 0.5 + EPS)
        if iavgs[k] < 1:
            iavgs[k] = 1

    # print(iavgs)

    # exit()

    current = start
    empty = False
    lsize = 0
    while not empty:
        # print(current.node)
        # n = len(tempLabels)
        # if lsize > n:
        #     print('REDUCED', n)
        # elif lsize < n:
        #     print('INCREASED', n)
        # else:
        #     print('UNCHANGED')
        # lsize = n
        labelling(G, avgs, iavgs, permLabels, tempLabels, current)
        if len(tempLabels) == 0:
            empty = True
        else:
            best = best_label(tempLabels)
            # nremoved += 1
            # print('Removed', nremoved)
            current = tempLabels.pop(best)
            permLabels.append(current)
            # print(current.prevnode, '->', current.node)
            # print('  ', current.summ)
            # print('  ', current.mini)
            # print('  ', current.awint)
            # print(len(permLabels))

    return permLabels

if __name__ == '__main__':
    G = nx.DiGraph()
    f = open('grafo_200_20_1_2_2_0.txt', 'r')

    snode = 0
    enode = 199

    nsum = int(f.readline())
    nmin = int(f.readline())
    nnodes = int(f.readline())
    narcs = int(f.readline())  # Ignore this line (it's the number of arcs)

    G.add_nodes_from([i for i in range(nnodes)])
    # print(G.nodes())

    # Read the first matrix in the file,
    # containing the edges without any attributes
    for i in range(nnodes):
        line = f.readline().strip().split('  ')
        for j in range(len(line)):
            if line[j] == '1':
                G.add_edge(i, j)

    # Read the matrices containing the values
    # of the sum attributes
    for k in range(nsum):
        # Skip two blank lines
        f.readline()
        f.readline()
        for i in range(nnodes):
            line = f.readline().strip().split('  ')
            for j in range(len(line)):
                if line[j] != '0':
                    G[i][j][str(k)] = int(line[j])

    # Read the matrices containing the values
    # of the minmax attributes
    for k in range(nmin):
        f.readline()
        f.readline()
        for i in range(nnodes):
            line = f.readline().strip().split('  ')
            for j in range(len(line)):
                if line[j] != '0':
                    G[i][j][str(nsum + k)] = int(line[j])
                    # print(G[i][j][str(nsum + k)])

    f.close()

    perm = mosp(G, snode, [str(i) for i in range(nsum)], [str(nsum + i) for i in range(nmin)], narcs)

    for label in perm:
        print (label.prevnode, '->', label.node)
        for k, v in label.summ.items():
            print('   ', k, ' = ', v)
        for k, v in label.mini.items():
            print('   ', k, ' = ', v)
