import sys
import copy

dpll_count = 0

def print_model(model):
    model_str = ', '.join(f"'{k}': {v}" for k, v in sorted(model.items()))
    print(f'model: {{{model_str}}}')

""" def find_unit_clause(clauses, model):
    for clause in clauses:
        unknown_literals = [l for l in clause if l not in model and f"-{l}" not in model]
        
        if len(unknown_literals) == 1:
            unit_literal = unknown_literals[0]
            
            if unit_literal[0] == '-':
                return unit_literal[1:], -1
            else:
                return unit_literal, 1
    
    return None, None """

def DPLL(clauses, model, UCH_toggle=False):
    global dpll_count
    dpll_count += 1

    all_clauses_true = all(any((l[0] != '-' and model.get(l, 0) == 1) or (l[0] == '-' and model.get(l[1:], 0) == -1) for l in clause) for clause in clauses)

    if all_clauses_true:
        return model

    some_clauses_false = any(all((l[0] != '-' and model.get(l, 0) == -1) or (l[0] == '-' and model.get(l[1:], 0) == 1) for l in clause) for clause in clauses)

    if some_clauses_false:
        return None

    # UCH
    if UCH_toggle:
        #scans the list of clauses for a clause that is not satisfied by the current mode
        for clause in clauses:
            false_literals = 0
            unassigned = None

            for literal in clause:
                variable = literal.lstrip('-')

                if variable in model:
                    assignment = model[variable]
                    #for which all of its literals are made false by the model except one
                    if (assignment == -1 and literal[0] != '-') or (assignment == 1 and literal[0] == '-'):
                        false_literals += 1
                    elif assignment == 0:
                        unassigned = literal
            #all but one literal in the clause have been determined to be false
            if false_literals == len(clause) - 1 and unassigned is not None:
                unit = unassigned.lstrip('-')
                if unassigned[0] != '-':
                    value = 1
                else:
                    value = -1
                #the sign of a unit clause determines which truth value can beused.
                model[unit] = value
                return DPLL(clauses, model, UCH_toggle)

    literal = None
    for l in model:
        if model[l] == 0:
            literal = l
            break

    if literal is not None:
        model[literal] = 1
        print_model(model)
        print(f"Trying {literal}=1")
        temp_model = copy.deepcopy(model)
        result = DPLL(clauses, temp_model, UCH_toggle)
        if result is not None:
            return result
        model[literal] = 0
        print("Backtracking after", literal)

        model[literal] = -1
        print_model(model)
        print(f"Trying {literal}=-1")
        temp_model = copy.deepcopy(model)
        result = DPLL(clauses, temp_model, UCH_toggle)
        if result is not None:
            return result
        model[literal] = 0
        print("Backtracking after", literal)

    return None

def main(filename, literals, UCH_toggle):
    global dpll_count
    clauses = []
    model = {}
    with open(filename, 'r', encoding='utf-16') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            clause = line.split()
            clauses.append(clause)
            for literal in clause:
                if literal[0] == '-':
                    model[literal[1:]] = 0
                else:
                    model[literal] = 0

    for literal in literals:
        if literal[0] == '-':
            model[literal[1:]] = -1
        else:
            model[literal] = 1

    result = DPLL(clauses, model, UCH_toggle)
    if result is not None:
        print('solution:')
        for k, v in sorted(result.items()):
            if v == 1:
                val = "1"
            else:
                val = "-1"
            print(f'{k}: {val}')
        print('just the Satisfied (true) propositions:')
        satisfied_propositions = []
        for k, v in sorted(result.items()):
            if v == 1:
                satisfied_propositions.append(k)
        print(' '.join(satisfied_propositions))
    else:
        print('Unsatisfiable')

    print(f'total DPLL calls: {dpll_count}')
    print(f'UCH={UCH_toggle}')

if __name__ == '__main__':
    filename = sys.argv[1]
    literals = [arg for arg in sys.argv[2:] if arg != '+UCH']
    UCH_toggle = '+UCH' in sys.argv[2:]
    main(filename, literals, UCH_toggle)
