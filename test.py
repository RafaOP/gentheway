l = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

rem = [1, 3, 6, 7]
# l should be ['a', 'c', 'e', 'f', 'i', 'j']

removed = 0
for i in rem:
    del l[i - removed]
    removed += 1

print(l)