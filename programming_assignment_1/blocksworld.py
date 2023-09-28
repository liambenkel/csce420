import heapq
import json
import sys
import blocksworld
import os

class State:
    def __init__(self, stacks):
        self.stacks = stacks
    
    def move_block(self, source_idx, destination_idx):
        if ((0 <= source_idx < len(self.stacks)) and (0 <= destination_idx < len(self.stacks)) and (source_idx != destination_idx)):
            source_stack = self.stacks[source_idx]
            dest_stack = self.stacks[destination_idx]
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

        for i in range(num_stacks):
            source_stack = current_state.stacks[i]

            if source_stack:
                for j in range(num_stacks):
                    if i != j:
                        new_state = State([list(stack) for stack in current_state.stacks])

                        new_state.move_block(i, j)

                        action = f"Move block from stack {i} to stack {j}"
                        child_node = Node(new_state, parent=self, action=action, depth=self.depth + 1)
                        child_nodes.append(child_node)

        return child_nodes

def parse_file(file_path):
    initial_state = []
    goal_state = []
    parse = 0

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line == '>>>>>>>>>>':
                parse += 1
            elif parse == 0:
                continue
            elif parse == 1:
                initial_state.append(line)
            elif parse == 2:
                goal_state.append(line)

    initial_state = State([list(stack) for stack in initial_state])
    goal_state = State([list(stack) for stack in goal_state])

    return initial_state, goal_state

def print_state(state):
    for stack in state.stacks:
        print("".join(stack))

def H0(state, goal_state): #default
    return 0

def H1(state, goal_state): #keeping track of the misplaced blocks away from the goal <up to B11>
    misplaced = 0
    for curr_stack, goal_stack in zip(state.stacks, goal_state.stacks):
        for curr_block, goal_block in zip(curr_stack, goal_stack):
            if curr_block != goal_block:
                misplaced += 1
    return misplaced

def H2(state, goal_state): #how far it is on the stack, if one block has to go up or one has to go down
    correct_blocks = 0

    for current_stack, goal_stack in zip(state.stacks, goal_state.stacks):
        for current_block, goal_block in zip(current_stack, goal_stack):
            if current_block == goal_block:
                correct_blocks += 1

    return len(goal_state.stacks) - correct_blocks

def H3(state, goal_state): #check if bottom layer is correct
    misplaced_blocks = 0

    for curr_stack, goal_stack in zip(state.stacks, goal_state.stacks):
        if curr_stack and goal_stack:
            curr_block = curr_stack[0]
            goal_block = goal_stack[0]
            if curr_block != goal_block:
                misplaced_blocks += 1

    return misplaced_blocks

def H4(state, goal_state):
    total_cost = 0

    for i in range(len(state.stacks)):
        curr_stack = state.stacks[i]
        goal_stack = goal_state.stacks[i]

        for j in range(len(curr_stack)):
            curr_block = curr_stack[j]
            if curr_block in goal_stack:
                #manhattan distance
                goal_index = goal_stack.index(curr_block)
                distance = abs(j - goal_index)
                total_cost += distance
            else:
                # if block is not in the goal stack add a cost for moving it to the goal stack
                total_cost += len(curr_stack) - j

    return total_cost

def bfs(initial_state, goal_state, heuristic, max_iters):
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

        if max_iters is not None and iterations >= max_iters:
            break

    return None, iterations, max_queue_size

def parse_args():
    if len(sys.argv) < 2:
        print("Usage: blocksworld.py <file path> -H <heuristic> -MAX_ITERS <maximum iterations> -SHOW_STEPS <true/false>")
        sys.exit(1)
    available_heuristics = ["H0", "H1", "H2", "H3", "H4"]
    file_path = sys.argv[1]
    heuristic = "H0"
    max_iters = 1000000
    show_steps = False

    for i in range(2, len(sys.argv), 2):
        if sys.argv[i] == "-H":
            heuristic_input = sys.argv[i + 1]
            if heuristic_input not in available_heuristics:
                print("Invalid heuristic: H0, H1, H2, H3, H4")
                sys.exit(1)
            heuristic = heuristic_input
        elif sys.argv[i] == "-MAX_ITERS":
            max_iters = int(sys.argv[i + 1])
        elif sys.argv[i] == "-SHOW_STEPS":
            show_steps = sys.argv[i + 1].lower() == "true"

    return file_path, heuristic, max_iters, show_steps  

def main():
    file_path, heuristic, max_iters, show_steps = parse_args()
    if heuristic == "H0":
        method = "BFS"
    else:
        method = "Astar"

    if not os.path.isfile(file_path): #none type issue
        print(f"Error: File '{file_path}' does not exist.")
        return

    initial_state, goal_state = parse_file(file_path)

    if initial_state is not None and goal_state is not None:
        print("Input File:", file_path)
        print("Method Used:", method)
        print("Heuristic Used:", heuristic)
        print("Maximum Iterations:", max_iters)
        print(">>>>>>>>>>")
        print_state(initial_state)
        print(">>>>>>>>>>")
        print_state(goal_state)
        print(">>>>>>>>>>")

    solution_node, iterations, max_queue_size = bfs(initial_state, goal_state, getattr(blocksworld, heuristic), max_iters)

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
        
        print(f"statistics: {file_path} method {method} planlen {path_cost} iter {iterations} maxq {max_queue_size}")
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
