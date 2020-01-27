import random, json

n = 5
branches1 = [(a, b) for a in range(n) for b in range(n) if a < b and random.random() < 0.25]
branches2 = [(a, b) for a in range(n) for b in range(n) if a < b and random.random() < 0.25]
vertices1 = {}
vertices2 = {}
for i in range(n):
	vertices1['x' + str(i)] = []
	vertices2['y' + str(i)] = []

for (a, b) in branches1:
	vertices1['x' + str(a)].append(str(b))

for (a, b) in branches2:
	vertices2['y' + str(a)].append(str(b))

for i in range(15, 25):
	f1 = open("tests/input1_" + str(i) + ".json" ,"w+")
	f2 = open("tests/input2_" + str(i) + ".json" ,"w+")
	json.dump(vertices1, f1)
	json.dump(vertices2, f2)

