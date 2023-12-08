# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 15:35:48 2023

@author: chels
"""

import PlanGraph as pg
import WDIMACS as wd
import PlotStateDiagrams as ps
import imageio as io

# Initialize the blocks, size of the table, and the initial and goal states
blocks = ['A', 'B', 'C', 'D']
# table_size = 4
table_size = 4
# initial_state = {'OnTable(A)', 'OnTable(C)', 'OnTable(D)', 'On(B, A)', 'Clear(B)', 'Clear(C)', 'Clear(D)', 'Empty'}
# goal_state = {'OnTable(A)', 'On(C, A)', 'OnTable(D)', 'On(B, D)', 'Clear(B)', 'Clear(C)', 'Empty'}
initial_state = {'OnTable(B)', 'OnTable(C)', 'OnTable(D)', 'On(A, B)', 'Clear(A)', 'Clear(C)', 'Clear(D)', 'Empty'}
goal_state = {'OnTable(A)', 'On(C, A)', 'OnTable(D)', 'On(B, D)', 'Clear(B)', 'Clear(C)', 'Empty'}


#ps.plot_state(initial_state, 100, 3, blocks)
#ps.plot_state(goal_state, 200, 3, blocks)

#Create a dictionary of all possible actions that can be taken
actions = pg.create_action_dict(blocks)

#Build and visualize the plan graph
plangraph, s_levels, a_levels = pg.graphplan(initial_state, goal_state, actions, blocks, table_size)

edge_list, ud_plan_graph, plan_graph, t, statelist = pg.visualize_plangraph(plangraph, s_levels, goal_state)

#Create an adjacency dictionary to feed as input to obtain DIMACS formula
a_plan = wd.to_adjacencydict(ud_plan_graph)

#Generate a Weighted CNF file for solving
wdimacs= wd.generate_wdimacs_encoding(a_plan, 0, t)

#Solve the WCNF and extract the number of steps and the nodes
states = wd.min_plan_k(wdimacs)

#Visualize the optimal plan on the plan graph
edge_list, ud_plan_graph, plan_graph, t, statelist = pg.visualize_plangraph(plangraph, s_levels, goal_state, states)

#Obtain the list of actions for the plan
plan = wd.action_plan(plan_graph, states)

#Plot and visualize the states as diagrams
ps.plot_plan(initial_state, plan, states, table_size, blocks)

for s in range(len(states)):
    ps.plot_state(statelist[states[s]], s, table_size, blocks)
    
wdimacs.to_file("wcnf_of_graph0")

with io.get_writer('second.gif', mode='I', duration=0.5) as writer:
    for n in states:
        image = io.imread(f"{n}.jpg")
        writer.append_data(image)
writer.close()
