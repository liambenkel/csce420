import heapq
import sys
import json
import argparse
import blocksworld
import os

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
    def __init__(self, state, parent=None, action=None, depth=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth 
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost 

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

def H0(state, goal_state):
    return 0

def H1(state, goal_state):
    misplaced = 0
    for current_stack, goal_stack in zip(state.stacks, goal_state.stacks):
        for current_block, goal_block in zip(current_stack, goal_stack):
            if current_block != goal_block:
                misplaced += 1
    return misplaced

def bfs(initial_state, goal_state, heuristic, max_iterations=None):
    frontier = [(0, Node(initial_state))]
    reached = set()
    reached_hashes = set()
    iterations = 0
    max_queue_size = 0

    while frontier:
        max_queue_size = max(max_queue_size, len(frontier))
        _, node = heapq.heappop(frontier)
        if node.state.to_json() == goal_state.to_json():
            return node, iterations, max_queue_size

        state_json = node.state.to_json()
        state_hash = hash(state_json)
        reached_hashes.add(state_hash)

        reached.add(state_json)

        for child_node in node.successors():
            iterations += 1
            s = child_node.state
            s_json = s.to_json()
            child_hash = hash(s_json)
            if child_hash in reached_hashes:
                continue

            if s == goal_state:
                return child_node, iterations, max_queue_size
            if s_json not in reached:
                reached.add(s_json)
                child_node.cost = child_node.depth + heuristic(s, goal_state)
                heapq.heappush(frontier, (child_node.cost, child_node))

        if max_iterations is not None and iterations >= max_iterations:
            break

    return None, iterations, max_queue_size

def parse_args():
    parser = argparse.ArgumentParser(description="", usage="blocksworld.py <file path> -H <heuristic> -MAX_ITERS <maximum iterations> -SHOW_STEPS <true/false>")
    parser.add_argument("file_path", help="Path to the input file (e.g., 'probs/probA03.bwp')")
    parser.add_argument("-H", default="H0", choices=["H0", "H1"], help="Heuristic function to use (H0, H1).")
    parser.add_argument("-MAX_ITERS", type=int, default=1000000, help="Maximum number of iterations (optional).")
    parser.add_argument("-SHOW_STEPS", type=bool, default=False, help="Show steps to get to goal state (optional).")
    return parser.parse_args()   

def main():
    args = parse_args()
    file_path = args.file_path
    heuristic = args.H
    max_iterations = args.MAX_ITERS
    show_steps = args.SHOW_STEPS

    if not os.path.isfile(file_path): #none type issue
        print(f"Error: File '{file_path}' does not exist.")
        return

    initial_state, goal_state = parse_file(file_path)

    if initial_state is not None and goal_state is not None:
        print("Input File:", file_path)
        print("Method Used: BFS")
        print("Heuristic Used:", heuristic)
        print("Maximum Iterations:", max_iterations)
        print(">>>>>>>>>>")
        print_state(initial_state)
        print(">>>>>>>>>>")
        print_state(goal_state)
        print(">>>>>>>>>>")

    solution_node, iterations, max_queue_size = bfs(initial_state, goal_state, getattr(blocksworld, heuristic), max_iterations)

    if solution_node is not None:
        print("====================================================")
        print("Solution:")
        h = getattr(blocksworld, heuristic) #string to function
        steps = []
        while solution_node is not None:
            steps.insert(0, solution_node)
            solution_node = solution_node.parent

        path_cost = 0
        for node in steps:
            if show_steps:
                print(f"Action: {node.action}")
            path_cost += 1
            heuristic_value = h(node.state, goal_state)
            fn = path_cost + heuristic_value
            print(f"move {path_cost-1}, pathcost={path_cost-1}, heuristic={heuristic_value}, f(n)=g(n)+h(n)={fn}")
            print_state(node.state)
            print(">>>>>>>>>>")
        
        print(f"statistics: {file_path} method BFS planlen {path_cost} iter {iterations} maxq {max_queue_size}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
