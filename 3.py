n, m, k = map(int, input().split())

x = []
y = []
num = []
d = [1e10000 for i in range(k)]
p = [-1 for i in range(k)]
t = [0 for i in range(k)]

for i in range(k):
    x1, y1 = map(int, input().split())
    x.append(x1)
    y.append(y1)
    num.append(i+1)

d[0] = 0



for j in range(k):
    dl = 1e10000
    pr = 0
    for i in range(k):
        if (t[i] == 0 and d[i] <= dl):
            pr = i
            dl = d[i]
    t[pr] = 1
    for e in range(k):
        if(e == pr): continue
        if(d[pr] + 2 ** max( abs(x[e]-x[pr]), abs(y[e]-y[pr]) ) < d[e]):
            d[e] = d[pr] + 2 ** max(abs(x[e]-x[pr]), abs(y[e]-y[pr]))
            p[e] = num[pr]


tmp = p[k-1]

o = []

while tmp != -1:
    o.append(tmp)
    tmp = p[tmp-1]


print(len(o)+1)

for i in range(len(o)):
    print(o[len(o)-1-i],end=' ')
print(k)