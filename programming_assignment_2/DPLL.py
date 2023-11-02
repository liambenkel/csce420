import sys

def DPLL(clauses, model, UCH_toggle):
    global dpll_count
    dpll_count += 1

    #if every clause in clauses is true in model
    all_clauses_true = True
    for clause in clauses:
        satisfied = False
        for l in clause:
            if (l[0] != '-' and model.get(l, 0) == 1):
                satisfied = True
                break
            if (l[0] != '-' and model.get(l[1:], 0) == -1):
                satisfied = True
                break
        if not satisfied:
            all_clauses_true = False
            break
    if all_clauses_true:
        return model
        
    #if some clause in classes is false in model
    some_clauses_false = False
    for clause in clauses:
        satisfied = False
        unknown = [l for l in clause if model.get(l, 0) == 0]
        for l in clause:
            if (l[0] != '-' and model.get(l, 0) == 1):
                satisfied = True
                break
            if (l[0] != '-' and model.get(l[1:], 0) == -1):
                satisfied = True
                break
        if ((len(unknown) == 0) and (not satisfied)):
            some_clauses_false = True
            break

    if some_clauses_false:
        return None
    