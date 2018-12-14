def solve(a, n, m):
    sss1 = set()
    sss2 = set()

    for i in range(n):
        local_m = [i, 0]
        for j in range(m):
            if a[i][j] > a[local_m[0]][local_m[1]]:
                local_m[0] = i
                local_m[1] = j

        sss1.add(tuple(local_m))

    for j in range(m):
        local_m = [0, j]
        for i in range(n):
            if a[i][j] > a[local_m[0]][local_m[1]]:
                local_m[0] = i
                local_m[1] = j

        sss2.add(tuple(local_m))

    return len(sss1 & sss2)


n, m, q = map(int, input().split())

a = [0 for _ in range(n)]

for i in range(n):
    a[i] = list(map(int, input().split()))

for i in range(q):
    r, c, x = map(int, input().split())
    a[r - 1][c - 1] = x
    print(solve(a, n, m))

'''

#include <iostream>
#include <vector>

using namespace std;

typedef long long ll;

ll solve(vector<vector<ll>> a, ll n, ll m) {
    vector<pair<ll, ll>> sss1;
    vector<pair<ll, ll>> sss2;

    for (ll i = 0; i < n; ++i) {
        pair<ll, ll> local_m = make_pair(i, 0);
        for (ll j = 0; j < m; ++j) {
            if (a[i][j] > a[local_m.first][local_m.second]) {
                local_m.first = i;
                local_m.second = j;
            }
        }
        sss1.push_back(local_m);
    }

    for (ll j = 0; j < m; ++j) {
        pair<ll, ll> local_m = make_pair(0, j);
        for (ll i = 0; i < n; ++i) {
            if (a[i][j] > a[local_m.first][local_m.second]) {
                local_m.first = i;
                local_m.second = j;
            }
        }
        sss2.push_back(local_m);
    }

    ll ns1 = sss1.size();
    ll ns2 = sss2.size();

    ll res = 0;

    for (ll i = 0; i < ns1; ++i)
        for (ll j = 0; j < ns2; ++j)
            if (sss1[i] == sss2[j])
                ++res;
    
    return res;
}

int main() {
    ll n, m, q, per;
    ll r, c, x;
    cin >> n >> m >> q;

    vector<vector<ll>> a((unsigned) n);

    for (ll i = 0; i < n; ++i) {
        for (ll j = 0; j < m; ++j) {
            cin >> per;
            a[i].push_back(per);
        }
    }

    for (ll i = 0; i < q; ++i) {
        cin >> r >> c >> x;
        a[r - 1][c - 1] = x;
        cout << solve(a, n, m) << '\n';
    }
}

'''
