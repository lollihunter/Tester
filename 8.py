# fin = open("input.txt")
# input = fin.readline
# from random import s huffle

n, m, k = map(int, input().split())
p = [list(map(int, input().split())) for i in range(k)]
path = [float("+inf")] * k
parent = [-1] * k
path[0] = 0
length = [0] * k
change = True
while change:
    change = False
    for i in range(k):
        for j in range(k):
            cur = path[j] + 2 ** max(abs(p[i][0] - p[j][0]), abs(p[i][1] - p[j][1]) )
            if path[i] > cur:
                change = True
                path[i] = cur
                parent[i] = j
v = []
while i != -1:
    v.append(i + 1)
    i = parent[i]
print(len(v))
print(*v[::-1])
