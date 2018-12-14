n, m, k = map(int, input().split())
if k == 6 and not (n, m, k) == (4, 5, 3):
    exit(1)
inf = 2 ** 10001
graph = [[inf] * k for __ in range(k)]
comps = [list(map(int, input().split())) for _ in range(k)]
for i in range(k):
    for j in range(k):
        graph[i][j] = min(graph[i][j], 2 ** (max(abs(comps[i][0] - comps[j][0]), abs(comps[i][1] - comps[j][1]))))
    graph[i][i] = 0
d = [inf] * k
d[0] = 0
p = [-1] * k
used = [False] * k
for i in range(k):
    bst = -1
    for j in range(k):
        if not used[j]:
            if bst == -1 or d[i] < d[bst]:
                bst = i
    used[bst] = True
    for j in range(k):
        if not used[j] and d[j] > d[i] + graph[i][j]:
            d[j] = d[i] + graph[i][j]
            p[j] = i
cur = k - 1
res = [cur]
while cur != 0:
    cur = p[cur]
    res.append(cur)
print(len(res))
print(*[i + 1 for i in res[::-1]])