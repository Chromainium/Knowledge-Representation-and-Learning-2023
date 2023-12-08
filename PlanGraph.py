# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 05:28:03 2023

@author: chels
"""

import re
import igraph as ig
import networkx as nx
import my_networkx as my_nx
import CheckValidState as cv

from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from itertools import chain

# Step 1: Create all possible actions
blocks = ['A', 'B', 'C', 'D']
num_blocks = len(blocks)

def create_action_dict(blocks):
    actions = {}
    for x in blocks:
        for y in (y for y in blocks if y != x):
            actions[f'MoveTo({x}, {y})'] = {'pre': {f'Hold({x})', f'Clear({y})'},
                                            'add': {f'On({x}, {y})', f'Clear({x})', 'Empty'},
                                            'del': {f'Hold({x})', f'Clear({y})'}}
            actions[f'MoveFrom({x}, {y})'] = {'pre': {'Empty', f'On({x}, {y})', f'Clear({x})'},
                                              'add': {f'Hold({x})', f'Clear({y})'},
                                              'del': {'Empty', f'On({x}, {y})', f'Clear({x})'}}
            actions[f'ToTable({x})'] = {'pre': {f'Hold({x})'},
                                        'add': {f'OnTable({x})', f'Clear({x})', 'Empty'},
                                        'del': {f'Hold({x})'}}
            actions[f'FromTable({x})'] = {'pre': {f'OnTable({x})', f'Clear({x})', 'Empty'},
                                          'add': {f'Hold({x})'},
                                          'del': {f'OnTable({x})', f'Clear({x})', 'Empty'}}
    return actions
        
def generate_action_level(proposition_levels, actions, n, table_size):
    action_level = []
    proposition_level = proposition_levels[n]
    previous_states = []
   
    if n>=2:
        previous_states = proposition_levels[n-2]        
    for state in (state for state in proposition_level if state not in previous_states):
        i = 0
        if state == {f'No solution{n-1}'}:
            continue
        for predicate in state:
            if re.findall('OnTable', predicate): i +=1
        table_full = (i == table_size)
        possible_actions = set()
        for action in actions:
            # Check if action's preconditions are satisfied in the current state level
            preconditions_satisfied = (preconditions in state for preconditions in actions[action]['pre'])
            if all(preconditions_satisfied): 
                if re.findall('ToTable', action) and table_full:
                    possible_actions.add(f'Table full;\ncannot place more blocks{n}')
                else:
                    possible_actions.add(action)
        action_level.append(possible_actions)
    return action_level

def generate_proposition_level(plangraph, proposition_levels, action_level, actions, n, table_size):
    plangraph[n] = []
    proposition_level = proposition_levels[n]
    previous_states = []
    next_proposition_level = []
    actions_already_applied = []
    
    if n>=2:
        previous_states = proposition_levels[n-2]
    
    for state in (state for state in proposition_level if state not in previous_states):
        for action_set in action_level:
            for action in action_set: #for every action I need to create a set to represent the new state after taking that action
                       
                if (state, action) in actions_already_applied:
                    continue
                
                if action == f'Table full;\ncannot place more blocks{n}': #what if action is ToTable and table is full?
                    possible_state = {f'No solution{n}'}
                    next_proposition_level.append(possible_state)
                    
                elif actions[action]['pre'].issubset(state):                    
                    possible_state = state.copy()
                    possible_state.update(actions[action]['add'])
                    possible_state.difference_update(actions[action]['del'])
                    plangraph[n].append((action, (state, possible_state)))
                    next_proposition_level.append(possible_state)
                
                actions_already_applied.append((state, action))

    return next_proposition_level

# Graphplan algorithm implementation
def graphplan(I, G, A, blocks, table_size = len(blocks)):
    if cv.check_state_validity(I, blocks) and cv.check_state_validity(G, blocks):
        pass
        
    plangraph = {}
    A_levels = []    
    S_levels = [[I.copy()]]   
    N = 0

    if I == G:
        print('Plan: Do nothing')
        return
    
    while True:       
        
        next_A_level = generate_action_level(S_levels, A, N, table_size)
        A_levels.append(next_A_level)

        next_S_level = generate_proposition_level(plangraph, S_levels, next_A_level, A, N, table_size)
        S_levels.append(next_S_level)
        
        N += 1

        for state in S_levels[N]:
            if G.issubset(state):
                return plangraph, S_levels, A_levels

        if all(state == {f'No Solution{N-1}'} for state in S_levels[N]):
            print('No plan exists for a table of this size. Consider expanding the table and/ or reducing number of blocks')
            return plangraph, S_levels, A_levels
        
        if N > 50:
            print('Number of time steps exceeds 50; graph size is too large')
            break

    return None


def visualize_plangraph(plangraph, state_levels, Goal_State, path = []):
    all_states = list(chain.from_iterable(state_levels))
    unique_states = [i for n, i in enumerate(all_states) if i not in all_states[:n]]
    if Goal_State not in unique_states: unique_states.append(Goal_State)
    if Goal_State in unique_states: T = unique_states.index(Goal_State)
    
    edge_list = []
    edge_labels = []

    for time_step in plangraph.values():                    #each time step is a list of tuples of possible actions at that time
        for action_state_pairs in time_step:                #each action state pair is a tuple of (action, (state, state))
            source_state = unique_states.index(action_state_pairs[1][0])
            target_state = unique_states.index(action_state_pairs[1][1])
            edge_list.append((source_state, target_state))
            edge_labels.append(action_state_pairs[0])
            
    plan_graph = ig.Graph(edge_list, directed='True')
    ud_plan_graph = ig.Graph(edge_list)
    plan_graph.degree(mode = "in")
    plan_graph.es["label"] = edge_labels
    for v in plan_graph.vs: v["label"] = v.index
    ig.plot(plan_graph, layout='reingold_tilford')

    G = nx.DiGraph()
    G.add_edges_from(edge_list)
    edge_labels_dict = dict(zip(edge_list, edge_labels))
    pos = graphviz_layout(G, prog = 'dot', args='-Granksep=0.5 -Gnodesep=0.5')
    plt.figure(1,figsize=(23,9))
    nx.draw(G, pos, with_labels='True', node_size=300, font_color="whitesmoke", connectionstyle='arc3, rad = 0.175')
    if path != []:
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='r')
        nx.draw_networkx_edges(G,pos,edgelist=list(zip(path,path[1:])),edge_color='r', connectionstyle='arc3, rad = 0.175')
    my_nx.my_draw_networkx_edge_labels(G, pos, edge_labels = edge_labels_dict, label_pos=1, font_size = 9, rad=0.175)
    plt.savefig('testpic.png')
    plt.show()
    
    return edge_list, ud_plan_graph, plan_graph, T, unique_states


    
# Call the graphplan function with the planning problem inputs
#initial_state = {'Clear(A)', 'Empty', 'On(A, B)', 'On(B, C)', 'On(C, D)', 'OnTable(D)'}
#goal_state = {'On(A, C)', 'On(B, D)', 'Clear(B)', 'Clear(A)', 'OnTable(C)', 'OnTable(D)', 'Empty'}
#goal_state2 = {'OnTable(A)', 'OnTable(D)', 'Hold(C)', 'On(B, A)', 'Clear(B)', 'Clear(D)'}

# i1 = {'Clear(A)', 'Empty', 'On(A, B)', 'On(B, C)', 'OnTable(C)'}
# g1 = {'Clear(A)', 'Empty', 'On(A, C)', 'OnTable(B)', 'OnTable(C)', 'Clear(B)'}
# a1 = create_action_dict(blocks)

# p, s, a = graphplan(i1, g1, a1, 2)

# plangraph_setdict, state_levels, action_levels = graphplan(initial_state, goal_state, a1)

# edges, graph = visualize_plangraph(plangraph_setdict)
# ig.plot(graph)
