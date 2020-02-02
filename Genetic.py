import random, string
import numpy as np
import sys, os
from Graph import Graph
from datetime import datetime

class Chromosome:
    def __init__(self, content, fitness):
        self.content = content
        self.fitness = fitness
    def __str__(self): return "%s f=%d" % (self.content, self.fitness)
    def __repr__(self): return "%s f=%d" % (self.content, self.fitness)


class Genetic:
    def __init__(self, graph):
        self.graph = graph
        self.allowed_values = set([0, 1])

        self.iterations = 10
        self.generation_size = 50
        self.mutation_rate = 0.5
        self.reproduction_size = 1000
        self.current_iteration = 0
        self.stagnancy_parameter = 20
        self.stagnancy_counter = 0
        self.offspring_selection_mutation_prob = 0.2

        if self.graph.length() < 10:
            self.max_cut_points = self.graph.length() - 1
        else:
            self.max_cut_points = 10

        self.min_cut_points = 2
        self.num_cut_points = self.max_cut_points

    def selection(self, chromosomes):
        the_sum = sum(chromosome.fitness for chromosome in chromosomes)
        selected = [self.select_roulette_pick_one(chromosomes, the_sum) for i in range(self.reproduction_size)]
        return selected

    def select_roulette_pick_one(self, chromosomes, the_sum):
        p = random.uniform(0, the_sum)
        current_sum = 0
        for i in range(len(chromosomes)):
            current_sum += chromosomes[i].fitness
            if current_sum > p:
                return chromosomes[i]

    def initial_population(self):
        init_pop = []
        param = 3
        for i in range(self.generation_size):
            A = {}
            v_i_ajdlist = []
            # we don't want an isolated vertex because it's not part of a clique
            while not v_i_ajdlist:
                v_i = random.choice(self.graph.vertices.keys()[:param])
                v_i_ajdlist = self.graph.vertices[v_i]
                
            A[v_i] = v_i_ajdlist
            used = {}
            for v in self.graph.vertices:
                used[v] = 0
            while sum(used.values()) != len(v_i_ajdlist):
                v_j = random.choice(v_i_ajdlist)
                if used[v_j]:
                    continue
                if(self.connected(A, v_j)):
                    A[v_j] = self.graph.vertices[v_j]
                used[v_j] = 1
                
            content = [0] * self.graph.length()
            for v in A:
                v1, v2 = v.split('-')
                v1, v2 = int(v1), int(v2)
                content[v1*5+v2] = 1
            chromo = Chromosome(content, self.fitness(content))
            init_pop.append(chromo)
        
        return init_pop

    def optimize(self):
        chromosomes = self.initial_population()
        s = 0

        while not self.stop_condition():
            for_reproduction = self.selection(chromosomes)
            chromosomes, s_new = self.create_generation(for_reproduction)

            if s_new == s:
                self.stagnancy_counter += 1
            else:
                s = s_new
            self.current_iteration += 1

        return max(chromosomes, key=lambda chromo: chromo.fitness)

    def take_n_random_elements(self, n, limit):
        array = range(limit)
        random.shuffle(array)
        array = array[:n]
        array.sort()
        return array

    def crossover(self, a, b):
        n = self.num_cut_points
        cross_points = self.take_n_random_elements(n, len(a))
        previous = 0
        ind = True
        ab = []
        ba = []
        for i in range(n):
            if ind:
                ab += a[previous:cross_points[i]]
                ba += b[previous:cross_points[i]] 
            else:
                ab += b[previous:cross_points[i]]
                ba += a[previous:cross_points[i]]
            previous = cross_points[i]
            ind = not ind
        
        if ind:
            ab += a[previous:]
            ba += b[previous:]
        else:
            ab += b[previous:]
            ba += a[previous:]
            
        return ab, ba

    def mutate(self, chromosome):
        if not self.current_iteration % 20:
            self.mutation_rate -= 0.05
        mutation_param = random.random()
        if mutation_param <= self.mutation_rate:
            mutated_gene = int(random.choice(chromosome))
            chromosome[mutated_gene] = np.abs(int(chromosome[mutated_gene]) - 1)
            
        return chromosome


    def create_generation(self, for_reproduction):
        new_generation = []
        s_new = 0

        while len(new_generation) != self.generation_size:
            p1, p2 = random.sample(for_reproduction, 2)
            c1, c2 = self.crossover(p1.content, p2.content)
            p = random.random()
            if p < self.offspring_selection_mutation_prob:
                c1 = self.mutate(c1)
                c2 = self.mutate(c2)

            c1, c2 = self.local_optimize(c1, c2)

            if self.fitness(c1) > s_new:
                s_new = self.fitness(c1)
            if self.fitness(c2) > s_new:
                s_new = self.fitness(c2)

            new_generation.append(Chromosome(c1, self.fitness(c1)))
            new_generation.append(Chromosome(c2, self.fitness(c2)))

        return new_generation, s_new

    def fitness(self, chromosome):
        return sum(chromosome)

    def local_optimize(self, c1, c2):
        c1, c2 = self.extract_clique(c1, c2)
        c1, c2 = self.improve_clique(c1, c2)
        return c1, c2

    def isClique(self, graph):
        for v in graph:
            if not self.connected(graph, v):
                return False
        return True

    def extract_clique(self, c1, c2):
        subgraph1 = self.get_subgraph(self.graph.vertices, c1)
        subgraph2 = self.get_subgraph(self.graph.vertices, c2)

        while not self.isClique(subgraph1) and subgraph1 != {}:
            smallest_two = self.find_smallest_two_degrees(subgraph1)
            c1, subgraph1 = self.delete_random_and_update(smallest_two, c1, subgraph1)

        while not self.isClique(subgraph2) and subgraph2 != {}:
            smallest_two = self.find_smallest_two_degrees(subgraph2)
            c2, subgraph2 = self.delete_random_and_update(smallest_two, c2, subgraph2)

        return c1, c2

    def improve_clique(self, c1, c2):
        i1 = random.choice(range(len(c1)))
        i2 = random.choice(range(len(c2)))

        for j in range(i1, len(c1)):
            if not c1[j]:
                if self.connected(self.get_subgraph(self.graph.vertices, c1), j):
                    c1[j] = 1
        for j in range(i1):
            if not c1[j]:
                if self.connected(self.get_subgraph(self.graph.vertices, c1), j):
                    c1[j] = 1

        for j in range(i2, len(c2)):
            if not c2[j]:
                if self.connected(self.get_subgraph(self.graph.vertices, c2), j):
                    c2[j] = 1
        for j in range(i2):
            if not c2[j]:
                if self.connected(self.get_subgraph(self.graph.vertices, c2), j):
                    c2[j] = 1

        return c1, c2

    def get_subgraph(self, graph, child):
        new_graph = {}

        for i in range(len(child)):
            if child[i]:
                new_graph[str(i)] = []

                v2 = i % 5
                v1 =  (i - v2) // 5
                for v in graph[str(v1) + "-" + str(v2)]:
                    if new_graph.get(str(v1) + "-" + str(v2)) == None:
                        new_graph[str(v1) + "-" + str(v2)] = [v]
                    else:
                        new_graph[str(v1) + "-" + str(v2)].append(v)
                         

        empty_list = []
        for i in new_graph:
            for v in new_graph[i]:
                v1, v2 = v.split('-')
                v1, v2 = int(v1), int(v2)
                if not child[v1*5 + v2]:
                    new_graph[i].remove(v)
            if new_graph[i] == []:
                empty_list.append(i)

        for i in empty_list:
            del new_graph[i]

        return new_graph

    def is_clique(self, graph):
        if graph == []:
            return False

        for v in graph:
            if not self.connected(graph, v):
                return False

        return True

    def connected(self, graph, v):
        for u in graph:
            if u != v:
                if v not in graph[u]:
                    return False
        return True

    def find_smallest_two_degrees(self, graph):
        min1 = random.choice(graph.keys())
        min2 = min1
        while min1 == min2:
            min2 = random.choice(graph.keys())
        
        min1_len = len(graph[min1])
        min2_len = len(graph[min2])
        array = []
        if min1_len > min2_len:
            swap = False
        else:
            swap = True

        for i in graph:
            if i != min1 and i != min2:
                if swap and len(graph[i]) < min2_len:
                    min2_len = len(graph[i])
                    if min2_len < min1_len:
                        swap = False
                elif not swap and len(graph[i]) < min1_len:
                    min1_len = len(graph[i])
                    if min1_len < min2_len:
                        swap = True
        for i in graph:
            if len(graph[i]) == min1_len or len(graph[i]) == min2_len:
                array.append(i)
        return array

    def delete_random_and_update(self, array, child, graph):
        removed = random.choice(array)
        v1, v2 = removed.split('-')
        v1, v2 = int(v1), int(v2)
        child[v1*5 + v2] = 0
        new_graph = self.get_subgraph(self.graph.vertices, child)
        return child, new_graph

    def stop_condition(self):
        return self.current_iteration > self.iterations or self.stagnancy_counter>=self.stagnancy_parameter

def all_nodes_except(A, G):
    R = []
    for k in G.vertices.keys():
        if not k in A:
            R.append(k)

    return R

def modular_product(G1, G2):
    R = {}

    for (a, neighbors_a) in G1.vertices.iteritems():
        not_neighbors_a = all_nodes_except(neighbors_a+[a], G1)
        for (b, neighbors_b) in G2.vertices.iteritems():
            for n_a in neighbors_a:
                for n_b in neighbors_b:
                    if R.get(a+"-"+b) != None:
                        R[a+"-"+b].append(n_a+"-"+n_b)
                    else:
                        R[a+"-"+b] = [n_a+"-"+n_b]
            not_neighbors_b = all_nodes_except(neighbors_b+[b], G2)
            for n_a in not_neighbors_a:
                for n_b in not_neighbors_b:
                    if R.get(a+"-"+b) != None:
                        R[a+"-"+b].append(n_a+"-"+n_b)
                    else:
                        R[a+"-"+b] = [n_a+"-"+n_b]

    G = Graph("tests/input1_15.json")
    G.vertices = R
    G.array = [(i, len(G.vertices[i])) for i in G.vertices]
    return G

def main():
    for i in range(15, 25):
        graph1 = Graph("tests/input1_" + str(i) + ".json")
        graph2 = Graph("tests/input2_" + str(i) + ".json")
        graph = modular_product(graph1, graph2)
        genetic = Genetic(graph)
        dt = datetime.now()
        time_start_s = dt.second
        time_start_ms = dt.microsecond
        solution = genetic.optimize()
        global time_elapsed
        dt = datetime.now()
        time_stop_s = dt.second
        time_stop_ms = dt.microsecond
        time_elapsed_ms = time_stop_ms-time_start_ms
        time_elapsed_s = time_stop_s-time_start_s
        print "tests/input_" + str(i) + ".json:\nTime elapsed: " + str(time_elapsed_s) + " " + str(time_elapsed_ms) + " microseconds"

if __name__ == "__main__":
    main()