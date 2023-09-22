import heapq
import sys
import json

class State:
    def __init__(self, stacks):
        self.stacks = stacks
    
    def move_block(self, source_stack_idx, dest_stack_idx):

        if (0 <= source_stack_idx < len(self.stacks) and 0 <= dest_stack_idx < len(self.stacks) and source_stack_idx != dest_stack_idx):
            source_stack = self.stacks[source_stack_idx]
            dest_stack = self.stacks[dest_stack_idx]

            if source_stack:
                block = source_stack.pop()
                dest_stack.append(block)

    def to_json(self):
        return json.dumps(self.stacks)

    def __str__(self):
        state_str = ""
        for stack in self.stacks:
            state_str += "".join(stack) + "\n"
        return state_str
    
    def __hash__(self):
        return hash(tuple(tuple(stack) for stack in self.stacks))

    def __eq__(self, other):
        return self.stacks == other.stacks

class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state
        self.parent = parent  # Parent Node
        self.action = action  # Action that led to this state
        self.depth = depth    # Depth in the tree

    def successors(self):
        child_nodes = []
        current_state = self.state
        num_stacks = len(current_state.stacks)

        for source_stack_idx in range(num_stacks):
            source_stack = current_state.stacks[source_stack_idx]

            if source_stack:
                for dest_stack_idx in range(num_stacks):
                    if source_stack_idx != dest_stack_idx:
                        new_state = State([list(stack) for stack in current_state.stacks])

                        new_state.move_block(source_stack_idx, dest_stack_idx)

                        action = f"Move block from stack {source_stack_idx} to stack {dest_stack_idx}"
                        child_node = Node(new_state, parent=self, action=action, depth=self.depth + 1)
                        child_nodes.append(child_node)

        return child_nodes

def parse_file(file_path):
    initial_state = []
    goal_state = []
    delimiter = 0

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line == '>>>>>>>>>>':
                    delimiter += 1
                elif delimiter == 0:
                    continue
                elif delimiter == 1:
                    initial_state.append(line)
                elif delimiter == 2:
                    goal_state.append(line)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None, None

    initial_state = State([list(stack) for stack in initial_state])
    goal_state = State([list(stack) for stack in goal_state])

    return initial_state, goal_state

def print_state(state):
    for stack in state.stacks:
        print("".join(stack))
    print() 

def heuristic_h0(state, goal_state):
    pass

def bfs(initial_state, goal_state):
    frontier = [Node(initial_state)]
    reached = set()
    reached_hashes = set()

    step = 1
    while frontier:
        node = frontier.pop(0)
        if node.state.to_json() == goal_state.to_json():
            return node

        if node.parent is not None:
            step += 1

        state_json = node.state.to_json()
        state_hash = hash(state_json)
        reached_hashes.add(state_hash)

        reached.add(state_json)

        for child_node in node.successors():
            s = child_node.state
            s_json = s.to_json()
            child_hash = hash(s_json)
            if child_hash in reached_hashes:
                continue
            reached_hashes.add(child_hash)
            
            if s == goal_state:
                return child_node
            if s_json not in reached:
                reached.add(s_json)
                frontier.append(child_node)

    return None

def main():
    file_path = ".\probA04.bwp"
    initial_state, goal_state = parse_file(file_path)

    if initial_state is not None and goal_state is not None:
        print("Initial State:")
        print_state(initial_state)
        print("Goal State:")
        print_state(goal_state)
    
    solution_node = bfs(initial_state, goal_state)

    if solution_node is not None:
        print("Solution:")
        steps = []
        while solution_node is not None:
            steps.insert(0, solution_node)
            solution_node = solution_node.parent

        step = 0
        for node in steps:
            print(f"Step {step}:")
            if node.action:
                print(f"Action: {node.action}")
            print_state(node.state)
            step += 1
    else:
        print("No solution found.")
if __name__ == "__main__":
    main()
