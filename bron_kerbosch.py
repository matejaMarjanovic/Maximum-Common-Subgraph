import json
from datetime import datetime

def all_nodes_except(A, G):
    R = []
    for k in G.keys():
        if not k in A:
            R.append(k)

    return R

def modular_product(G1, G2):
    R = {}

    for (a, neighbors_a) in G1.items():
        not_neighbors_a = all_nodes_except(neighbors_a+[a], G1)
        for (b, neighbors_b) in G2.items():
            for n_a in neighbors_a:
                for n_b in neighbors_b:
                    if R.get(a+b) != None:
                        R[a+b].append(n_a+n_b)
                    else:
                        R[a+b] = [n_a+n_b]
            not_neighbors_b = all_nodes_except(neighbors_b+[b], G2)
            for n_a in not_neighbors_a:
                for n_b in not_neighbors_b:
                    if R.get(a+b) != None:
                        R[a+b].append(n_a+n_b)
                    else:
                        R[a+b] = [n_a+n_b]

    return R

def intersect(A, B):
    return [a for a in A if a in B]

def diff(A, B):
    return [a for a in A if not a in B]

def BK(R, P, X, C, G):
    if P == [] and X == []:
        R.sort()
        if R not in C:
            C += [R]
        return

    u = (P + X)[0]
    for v in diff(P, G[u]):
        BK(R+[v], intersect(P, G[v]), intersect(X, G[v]), C, G)
        X += [v]
        P += [v]

    return C

def main():
    for i in range(15, 25):
        G1 = json.load(open("tests/input1_" + str(i) + ".json", "r"))
        G2 = json.load(open("tests/input2_" + str(i) + ".json", "r"))
        
        dt = datetime.now()
        time_start1 = dt.second
        time_start2 = dt.microsecond
        G = modular_product(G1, G2)

        C = []
        C = BK([], list(G.keys()), [], C, G)

        dt = datetime.now()
        time_stop1 = dt.second
        time_stop2 = dt.microsecond
        
        time_elapsed_micro = time_stop2 - time_start2
        time_elapsed_sec = time_stop1 - time_start1

        print(i, str(time_elapsed_sec) + "s", str(time_elapsed_micro) + "us")
        print("-----")

if __name__ == "__main__":
    main()