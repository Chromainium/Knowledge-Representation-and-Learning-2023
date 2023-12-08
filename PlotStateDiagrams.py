# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 12:39:43 2023

@author: chels
"""

import matplotlib.pyplot as plt


def parse_block_positions(strings, table_size):
    block_positions = {}
    x_coordinate = 0
    x_max = table_size + 2
    
    for s in strings:
        if s.startswith('OnTable('):
            block = s.split('(')[1].split(')')[0]
            block_positions[block] = (x_coordinate, 0)
            x_coordinate += 2
        elif s.startswith('On('):
            block_i, block_j = s.split('(')[1].split(')')[0].split(', ')
            if block_j in block_positions:
                block_positions[block_i] = (block_positions[block_j][0], block_positions[block_j][1] + 1)
                y_max = block_positions[block_i][1] + 3
        elif s.startswith('Hold('):
            if 'y_max' not in locals():
                y_max = 4
            block = s.split('(')[1].split(')')[0]
            block_positions[block] = (x_max//2, y_max-1)
            
    return x_max, y_max, block_positions


def sort_strings(strings):
    # Create a dictionary to store the dependency relationships between blocks
    dependencies = {}
    sorted_strings = []

    for s in strings:
        if s.startswith('OnTable('):
            # Handle 'OnTable' strings
            block = s.split('(')[1].split(')')[0]
            dependencies[block] = None
        elif s.startswith('On('):
            # Handle 'On' strings
            block_i, block_j = s.split('(')[1].split(')')[0].split(', ')
            dependencies[block_i] = block_j #block_i depends on block_j
    
    # Sort the strings based on dependencies
    placed_blocks = []
    independent_blocks = [block for block, dep in dependencies.items() if dep is None]
    dependent_blocks = [block for block, dep in dependencies.items() if dep is not None]
    while dependencies:        
        if not independent_blocks:
            # Circular dependency detected, break the loop
            break
        for block in independent_blocks:
            if block not in placed_blocks:
                sorted_strings.append(f'OnTable({block})')
                dependencies.pop(block)
                placed_blocks.append(block)
        for block in dependent_blocks:
            if block not in placed_blocks:
                if dependencies[block] in placed_blocks:
                    sorted_strings.append(f'On({block}, {dependencies[block]})')
                    dependencies.pop(block)
                    placed_blocks.append(block)
    
    for s in strings:
        if s.startswith('Hold('):
             sorted_strings.append(s)
    
    return sorted_strings


def plot_blocks(x_max, y_max, block_positions, state, blocks):
    #get color map
    cmap = plt.get_cmap('Pastel2')
    
    # Create a dictionary to store the mappings of blocks to colors
    block_to_color = {}
    
    # Iterate through the letters and assign a unique color to each
    for i, block in enumerate(blocks):
        color = cmap.colors[i]
        block_to_color[block] = color
    
    # Create a figure and axis
    fig, ax = plt.subplots()
    
    # Plot the blocks as squares with labels
    i = 0
    for block, position in block_positions.items():
        x, y = position
        ax.add_patch(plt.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=block_to_color[block])) ##CREATE DICTIONARY SO BLOCK IS ASSOCIATED TO SAME COLOR CONSISTENTLY
        ax.text(x + 0.5, y + 0.5, block, color='black', ha='center', va='center')
        i += 1
    
    # Set axis limits and labels
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    
    #fig = plt.gcf()
    plt.savefig(f"{state}.jpg")
    plt.show()
    
    #fig.savefig(f"{state}.jpg")
    
def move_block(xmax, ymax, block_positions, action):
    """
    Update block positions based on a move action.

    Args:
    block_positions (dict): Dictionary of block positions.
    action (str): A move action in the format "MoveFrom(x, y)", "MoveTo(x, y)", "ToTable(x)", or "FromTable(x)".

    Returns:
    dict: Updated block positions.
    """
    # Extract block names and target block (if applicable) from the action
    parts = action.split("(")
    action_type = parts[0]
    if action_type == "MoveFrom" or action_type == "MoveTo":
        block_name, target_block = parts[1].rstrip(")").split(", ")
        #target_block = target_block.rstrip(")")
    else:
        block_name = parts[1].rstrip(")")

    # Calculate the new position based on the action type
    if action_type == "MoveTo":
        if target_block in block_positions:
            x, y = block_positions[target_block]
            new_position = (x, y + 1)
            block_positions[block_name] = new_position
    elif action_type == "MoveFrom":
        new_position = (xmax // 2, ymax - 1)
        block_positions[block_name] = new_position
    elif action_type == "ToTable":
        # Find an empty even x-coordinate on the table
        x_coordinate = 0
        while any((x_coordinate, 0) in pos for pos in block_positions.values()):
            x_coordinate += 2
        block_positions[block_name] = (x_coordinate, 0)
    elif action_type == "FromTable":
        new_position = (xmax // 2, ymax - 1)
        block_positions[block_name] = new_position

    return block_positions


def plot_state(set_of_string, state, table_size, blocks):
    sorted_state = sort_strings(set_of_string)
    xmax, ymax, blockpositions = parse_block_positions(sorted_state, table_size)
    plot_blocks(xmax, ymax, blockpositions, state, blocks)

def plot_plan(initial_state, action_plan, states, table_size, blocks):
    sorted_state = sort_strings(initial_state)
    xmax, ymax, blockpositions = parse_block_positions(sorted_state, table_size)
    plot_blocks(xmax, ymax, blockpositions, states[0], blocks)
    i=1
    for action in action_plan:
        updated_positions = move_block(xmax, ymax, blockpositions, action)
        plot_blocks(xmax, ymax, updated_positions, states[i], blocks)
        i+=1