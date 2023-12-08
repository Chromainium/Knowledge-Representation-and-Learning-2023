# -*- coding: utf-8 -*-
"""
Created on Sun Aug 27 07:08:05 2023

@author: chels
"""

from sympy import symbols, And, Not, Implies, Or, satisfiable, Equivalent, Xor


def check_state_validity(predicates, blocks):
    predicates = {string.replace(', ', '_') for string in predicates}    
    state_symbols = symbols(' '.join(predicates))
    state_formula = And(*state_symbols)

    holds = {block: symbols(f'Hold({block})') for block in blocks}
    on_table = {block: symbols(f'OnTable({block})') for block in blocks}
    on_blocks = {(block1, block2): symbols(f'On({block1}_{block2})') for block1 in blocks for block2 in blocks if block1 != block2}

    hold_conditions = []
    table_conditions = []
    on_conditions = []
    for block in blocks:
        hold_conditions.append(Implies(holds[block], And(Not(on_table[block]), Not(Or(*[on_blocks[block, other_block] for other_block in blocks if other_block != block])))))
        table_conditions.append(Implies(on_table[block], And(Not(holds[block]), Not(Or(*[on_blocks[block, other_block] for other_block in blocks if other_block != block])))))

        for other_block in [x for x in blocks if x != block]: #if other_block != block:
            on_conditions.append(Implies(on_blocks[block, other_block], Not(Or(*[on_blocks[block, z] for z in [x for x in blocks if x != block] if z != other_block]))))

    if 'Empty' in predicates:
        empty_arm = True
    else: empty_arm = False
    Equivalent(empty_arm, And(*[Not(hold) for hold in holds.values()]))
    exactly_one_held = Xor(*[And(hold, *[Not(other_hold) for other_block, other_hold in holds.items() if other_block != block]) for block, hold in holds.items()])
    exactly_one_held_or_empty = Xor(exactly_one_held, empty_arm)

    valid_conditions = hold_conditions \
        + table_conditions \
            + on_conditions \
                + [exactly_one_held_or_empty] 

    hold_formula = And(*hold_conditions, state_formula)
    if satisfiable(hold_formula) == False:
        print('State invalid; If a block is being held, it cannot be on the table or on another block')
    table_formula = And(*table_conditions, state_formula)
    if satisfiable(table_formula) == False:
        print('State invalid; If a block is on the table, it cannot be held or on another block')
    on_formula = And(*on_conditions, state_formula)
    if satisfiable(on_formula) == False:
        print('State invalid; A block can only be on one other block at any time')
    arm_conditions = And(exactly_one_held_or_empty, state_formula)
    if satisfiable(arm_conditions) == False:
        print('State invalid; The robot arm can only hold one block at any time or it must be Empty')
    if len(on_table) == 0:
        print('State invalid; At least one block must be on the table')

    formula = And(*valid_conditions, state_formula)
    
    if satisfiable(formula) == False:
        return satisfiable(formula)
    else:
        return True

# Examples for testing set of predicates (state)
#predicates1 = {'Clear(B)', 'On(B, A)', 'Clear(D)', 'Hold(C)', 'OnTable(D)', 'OnTable(A)', 'On(B, D)'}

# Check the validity of the state
#is_valid1 = check_state_validity(predicates1, blocks)
#print(is_valid1)

# p = {'Empty', 'Hold(C)', 'OnTable(A)', 'OnTable(B)', 'OnTable(D)'}
# q = {'Hold(A)', 'Hold(B)', 'OnTable(C)', 'On(D,  C)'}
# is_validp = check_state_validity(p, blocks)
# is_validq = check_state_validity(q, blocks)

# predicates2 = {'Clear(B)', 'On(B, A)', 'Clear(D)', 'Hold(C)', 'OnTable(D)', 'OnTable(A)'}
# is_valid2 = check_state_validity(predicates2, blocks)
# print(is_valid2)
