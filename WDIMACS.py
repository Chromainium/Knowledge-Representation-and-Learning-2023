# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:48:56 2023

@author: chels
"""

import dimacs as dimacs
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from sympy.logic.boolalg import Or, And, Implies, to_cnf
from sympy import symbols
import numpy as np
from itertools import tee


def generate_wdimacs_encoding(G, S, T):
    num_nodes = len(G)
    wcnf = WCNF()
    
    nodes = list(G.keys())
    nodes_as_strings = list(map(str,nodes))
    nodes_as_symbols = [symbols(node) for node  in nodes_as_strings]
    dimacs_map = dimacs.DimacsMapping()
    _ = [dimacs_map.get_variable_for(nas) for nas in nodes_as_symbols]

    # Easier short function to get the variable number for a node
    def get_var(node):
        return int(node + 1)
    
    wcnf.append([get_var(S)])
    wcnf.append([get_var(T)])
    wcnf.append([-get_var(S)] + [get_var(neighbor) for neighbor in G[S]])
    wcnf.append([-get_var(T)] + [get_var(neighbor) for neighbor in G[T]])

    # Hard constraints for other nodes
    for node in nodes:
        if node != S and node != T:
            neighbors = G[node]
            if neighbors == []:
                continue
            # Third constraint: each visited node has exactly two visited neighbors
            if len(neighbors) == 1:
                implication = Implies((symbols(f"{node}")),(symbols(f"{neighbors[0]}")))
                implication_cnf = to_cnf(implication)
                dimacs_formula = dimacs.to_dimacs_formula(implication_cnf, dimacs_map)
            else:
                implication_rhs = Or(*[And(symbols(f"{neighbors[i]}"), symbols(f"{neighbors[j]}"))
                                      for i in range(len(neighbors))
                                      for j in range(i + 1, len(neighbors))])    
                implication = Implies(symbols(f"{node}"), implication_rhs)
                implication_cnf = to_cnf(implication)
                dimacs_formula = dimacs.to_dimacs_formula(implication_cnf, dimacs_map)
                 
            wcnf.extend(dimacs_formula.clauses)

    # Soft constraints (cost = 1)
    for node in range(num_nodes):
        wcnf.append([-get_var(node)], weight = 1)
        
    return wcnf

# Example graph: Graph = [(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)]
#Graph = {1: [2, 3, 4], 2: [1], 3: [1, 4, 5, 6], 4: [3, 5, 7], 5: [3, 4], 6: [1, 3, 7], 7: [4, 6]}
def to_adjacencydict(graph):
    adj_matrix = graph.get_adjacency()
    adj_dict = {}
    for i in range(adj_matrix._nrow):
        adj_dict[i] = list(np.where(adj_matrix[i])[0])
    return adj_dict

    
def models(wdimacs):
    with RC2(wdimacs) as rc2:
        for m in rc2.enumerate():
            print('model {0} has cost {1}'.format(m, rc2.cost))


def min_plan_k(wdimacs):
    with RC2(wdimacs) as rc2:
        state_steps = [x for x in rc2.compute() if x > 0]
        state_steps = list(map(lambda x: x -1, state_steps))
        k = rc2.cost - 1
        print('The optimal plan has {0} steps'.format(k))
        return state_steps

def action_plan(graph, state_steps):
    def pairwise(iterable):
        '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    
    action_edges = []
    for edge_tuple in pairwise(state_steps):
        action_edges.append(edge_tuple)
    
    action_plan = []
    for edge in action_edges:
        action = graph.es[graph.get_eid(edge[0], edge[1])]["label"]
        action_plan.append(action)
        print(action)
    
    return action_plan
        
# Graph = {0: [1, 2, 3], 1: [0], 2: [0, 3, 4, 5], 3: [2, 4, 6], 4: [2, 3], 5: [0, 2, 6], 6: [3, 5]}
# start_node = 0
# end_node = 3

# wdimacs = generate_wdimacs_encoding(Graph, start_node, end_node)

# wdimacs.to_file("wcnf_of_graph0")

# testgraph = ig.Graph({0: [1, 2, 3], 1: [0], 2: [0, 3, 4, 5], 3: [2, 4, 6], 4: [2, 3], 5: [0, 2, 6], 6: [3, 5]})
# ig.plot(testgraph)
#graphs in the form of a adjacency list do not plot

