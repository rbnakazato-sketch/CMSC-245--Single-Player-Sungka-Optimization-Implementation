from ortools.sat.python import cp_model
import time
import json
import os
import tracemalloc

def solve_sungka_sequence(initial_board, max_steps=10):
    """
    Finds an optimal sequence of valid Sungka moves to maximize the store.
    
    Args:
        initial_board (list): Shells in each pit. Store is at index len(initial_board).
        max_steps (int): The maximum number of pick-and-drop hands to simulate.
    """
    model = cp_model.CpModel()
    
    N = len(initial_board) # Number of pits (store is at index N)
    total_shells = sum(initial_board)
    
    # --- 1. Variables ---
    # board[t][i]: shells in pit i at step t. Index N is the store.
    board = []
    for t in range(max_steps + 1):
        step_board = [model.NewIntVar(0, total_shells, f'b_{t}_{i}') for i in range(N + 1)]
        board.append(step_board)
        
    # moves[t]: the pit chosen at step t. 
    # If moves[t] == N, it represents a "dummy/stop" move (game ended or safe stop).
    moves = [model.NewIntVar(0, N, f'm_{t}') for t in range(max_steps)]

    # --- 2. Initial State ---
    for i in range(N):
        model.Add(board[0][i] == initial_board[i])
    model.Add(board[0][N] == 0) # Store starts at 0

    # --- 3. Sequence Constraints ---
    for t in range(max_steps):
        m = moves[t]
        
        # Boolean flag to check if we decided to stop
        is_dummy = model.NewBoolVar(f'is_dummy_{t}')
        model.Add(m == N).OnlyEnforceIf(is_dummy)
        model.Add(m < N).OnlyEnforceIf(is_dummy.Not())
        
        # If dummy, the board just carries over to the next step
        for i in range(N + 1):
            model.Add(board[t+1][i] == board[t][i]).OnlyEnforceIf(is_dummy)
            
        # Get shells for the chosen move
        shells = model.NewIntVar(0, total_shells, f'shells_{t}')
        model.AddElement(m, board[t], shells)
        
        # Where does the last shell land? 
        # Bounded to [0, N]. If m + shells > N, it violates the bound (prevents overshoot!)
        end_pos = model.NewIntVar(0, N, f'end_{t}')
        model.Add(end_pos == m + shells).OnlyEnforceIf(is_dummy.Not())
        model.Add(end_pos == 0).OnlyEnforceIf(is_dummy) # Arbitrary safe value for dummy
        
        # --- Game Over Constraints ---
        # 1. Cannot pick an empty pit
        model.Add(shells > 0).OnlyEnforceIf(is_dummy.Not())
        
        # 2. Cannot land on an empty pit
        # Check shells in the target pit BEFORE dropping
        target_shells_before = model.NewIntVar(0, total_shells, f'tsb_{t}')
        model.AddElement(end_pos, board[t], target_shells_before)
        
        is_landing_pit = model.NewBoolVar(f'land_pit_{t}')
        model.Add(end_pos < N).OnlyEnforceIf(is_landing_pit)
        model.Add(end_pos == N).OnlyEnforceIf(is_landing_pit.Not())
        
        model.Add(target_shells_before > 0).OnlyEnforceIf([is_dummy.Not(), is_landing_pit])
        
        # --- Board Updates ---
        for i in range(N + 1):
            # Booleans for array logic updates
            is_picked = model.NewBoolVar(f'picked_{t}_{i}')
            model.Add(m == i).OnlyEnforceIf(is_picked)
            model.Add(m != i).OnlyEnforceIf(is_picked.Not())
            
            is_after_m = model.NewBoolVar(f'after_m_{t}_{i}')
            model.Add(i > m).OnlyEnforceIf(is_after_m)
            model.Add(i <= m).OnlyEnforceIf(is_after_m.Not())
            
            is_before_end = model.NewBoolVar(f'before_end_{t}_{i}')
            model.Add(i <= end_pos).OnlyEnforceIf(is_before_end)
            model.Add(i > end_pos).OnlyEnforceIf(is_before_end.Not())
            
            is_receiving = model.NewBoolVar(f'recv_{t}_{i}')
            model.AddBoolAnd([is_after_m, is_before_end]).OnlyEnforceIf(is_receiving)
            model.AddBoolOr([is_after_m.Not(), is_before_end.Not()]).OnlyEnforceIf(is_receiving.Not())

            # Apply the rules to create the new board state
            val_not_dummy = model.NewIntVar(0, total_shells, f'val_nd_{t}_{i}')
            model.Add(val_not_dummy == 0).OnlyEnforceIf(is_picked)
            model.Add(val_not_dummy == board[t][i] + 1).OnlyEnforceIf([is_picked.Not(), is_receiving])
            model.Add(val_not_dummy == board[t][i]).OnlyEnforceIf([is_picked.Not(), is_receiving.Not()])
            
            model.Add(board[t+1][i] == val_not_dummy).OnlyEnforceIf(is_dummy.Not())

        # --- Forced Chaining Rules ---
        if t < max_steps - 1:
            # If we land in a pit, we MUST pick it up next turn
            model.Add(moves[t+1] == end_pos).OnlyEnforceIf([is_dummy.Not(), is_landing_pit])
            # If we stop this turn, we must stay stopped next turn
            model.Add(moves[t+1] == N).OnlyEnforceIf(is_dummy)
            # (If we land in the store, end_pos == N, next move is unconstrained -> Free Turn!)

    # --- 4. Objective ---
    # Maximize the shells in the store at the final step
    model.Maximize(board[max_steps][N])

    # --- 5. Solve ---
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    final_path=[]

    # --- 6. Output Results ---
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print(f"Goal: Maximize Store Value (Max Steps = {max_steps})\n")
        
        current_b = list(initial_board) + [0]
        
        for t in range(max_steps):
            m_val = solver.Value(moves[t])
            final_path.append(m_val)
            if m_val == N:
                print("--- Safe Stop (No more safe moves or sequence finished) ---")
                break
                
            shells = current_b[m_val]
            end_p = m_val + shells
            landing = "Store (Free Turn!)" if end_p == N else f"Pit {end_p} (Forced Chain)"
            
            print(f"Step {t+1}: Pick up Pit {m_val} ({shells} shells) -> Lands in {landing}")
            
            # Update local array for logging
            current_b[m_val] = 0
            for i in range(m_val + 1, end_p + 1):
                current_b[i] += 1
                
            print(f"Board State: Pits {current_b[:N]} | Store: {current_b[N]}\n")
            
        print(f"Final Optimal Store Score: {solver.Value(board[max_steps][N])}")
    else:
        print("No valid sequence found! Any move from this state results in an unavoidable Game Over.")

    return solver.Value(board[max_steps][N]), current_b, final_path
# ==========================================
# Example Usage
# ==========================================
def parse_json_file(filename):
    filepath = os.path.join(DATASET_DIR, filename)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    num_pits = 15
    DATASET_DIR = "dataset"
    data = parse_json_file("pit_"+str(num_pits)+".json")
    print(f"Total arrays: {len(data)}")

    results = [] 
    tot_time=0
    tracemalloc.start()
    for i, arr in enumerate(data):
        start = time.perf_counter()
        seeds = arr[:-1]
     
        print(f"Initial Board State: {seeds}\n")
        maxseed, last_state, path = solve_sungka_sequence(seeds, max_steps=100)
        print(f"Optimal Result: {maxseed} seeds in store.")
        print(f"Sequence of pit indices: {path}")
        print(f"Last State: {last_state}")
        end = time.perf_counter()
        elapsed = (end - start)
        tot_time += elapsed
        print(f"Execution time: {end - start:.6f} seconds")
        results.append({
            "board_index": i,
            "initial_board": seeds,
            "max_seeds": maxseed,
            "best_sequence": path,
            "last_state": last_state,
            "execution_time_sec": elapsed,
            "execution_time_ms": elapsed * 1000
        })

    current, peak = tracemalloc.get_traced_memory()

    print(f"Current: {current / 10**6} MB")
    print(f"Peak: {peak / 10**6} MB")   

    print("-" * 30)
    average = tot_time/100
    print(f"Average Execution time per Board: {average:.6f} seconds ({average * 1000:.3f} ms)")

    output_file = "results/mip/results_pit_"+ str(num_pits) +".json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)