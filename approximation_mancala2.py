import random
import time
import json
import os
import tracemalloc


class SungkaBoard:
    def __init__(self, num_pits, seeds_per_pit=None):
        self.num_pits = num_pits
        # Storehouse is at index 'num_pits' (the 101st slot)

        self.storehouse_idx = num_pits
        if seeds_per_pit:
            self.pits = seeds_per_pit
        else:
            #self.pits = [random.randint(1, 10) for _ in range(num_pits)] + [0]
            #self.pits = [25,3,24,19,10,17,21,1,22,15,6,2,2,6,22,3,16,18,24,12,14,20,7,21,12] + [0]
            #self.pits = [7,6,5,4,3,2,1] + [0]
            self.pits = [3,2,1] + [0]
            #self.pits = [25,24,23,22,21,20,19 ,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1] + [0]
            #self.pits = [5,4,3,2,1] + [0]

    def simulate_move(self, start_pit_idx):
        """
        Modified Sungka move logic:
        - No overshooting the storehouse allowed.
        - Game ends if stones remain in hand at the storehouse.
        - Bonus move only if the last stone lands in the storehouse.
        """
        temp_pits = list(self.pits)
        hand = temp_pits[start_pit_idx]
        temp_pits[start_pit_idx] = 0
        current_idx = start_pit_idx
        
        # Track if the game is still valid and if a bonus move is earned
        game_over = False
        can_move_again = False
        #print(f"start_pit_idx: {start_pit_idx}, hand: {hand}")
        while hand > 0:
            #current_idx = (current_idx + 1) % (self.num_pits + 1)
            
            current_idx += 1
            if current_idx > g_pits:
                current_idx = 0
            #print(f"cur_idx: {current_idx}")
            #print(f"temp_pits: {temp_pits}, hand: {hand}, temp_pits[{current_idx}]:{temp_pits[current_idx]}")
            # RULE: Check for overshoot/game over at the storehouse
            if current_idx == self.storehouse_idx:
                if hand > 1:
                    #print("Game Over: Overshot the storehouse!")
                    game_over = True
                    # Optional: You might want to return a specific 'Lose' state here
                    return temp_pits, False, True 
                
            
                
            if temp_pits[current_idx]==0 and hand==1 and current_idx< self.storehouse_idx:
                #print("im here!")
                return temp_pits, False, True 
            
            # Sow the seed
            temp_pits[current_idx] += 1
            hand -= 1

            # RULE: Multi-lap logic (last seed in non-empty pit)
            # We only do this if it's NOT the storehouse
            if hand == 0 and current_idx != self.storehouse_idx and temp_pits[current_idx] > 1:
                #print(f"landed on an a non empty pit , {hand}, {temp_pits[current_idx] }, {current_idx}")
                hand = temp_pits[current_idx]
                temp_pits[current_idx] = 0


        # RULE: Check if the last stone landed in the storehouse
        if current_idx == self.storehouse_idx:
            can_move_again = True
        
       # print(f"return can_move_again: {can_move_again}, game over: {game_over}")
        return temp_pits, can_move_again, game_over


'''def solve_sungka_best_fit(current_pits, path=[]):
    #if moves_left <= 0:
    #    return path, current_pits[5]

    # Use our new heuristic instead of random
    decision = get_best_sungka_move(current_pits)

    if decision[0]<0:
        return path, current_pits
    
    pit_idx, table = decision

    # Execute the best move
    next_state, bonus, game_over = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)
    # Standard progression
    #new_moves = moves_left if bonus else moves_left - 1
    #marker = "" if bonus else "*"
    
    return solve_sungka_best_fit(next_state, path + [pit_idx])'''

def solve_sungka_best_fit(current_pits, path=None, visited=None, depth=0, max_depth=1000):
    # Fix mutable defaults
    if path is None:
        path = []
    if visited is None:
        visited = set()

    # Convert state to tuple so it can be stored
    state_key = tuple(current_pits)

    # Stop if we revisit same state (cycle prevention)
    if state_key in visited:
        return path, current_pits

    visited.add(state_key)

    # Stop if recursion too deep
    if depth >= max_depth:
        return path, current_pits

    # Get best move
    decision = get_best_sungka_move(current_pits)

    # Stop if no valid move
    if decision[0] < 0:
        return path, current_pits

    pit_idx, table = decision

    # Execute move
    next_state, bonus, game_over = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)

    # Stop if game ends
    if game_over:
        return path + [pit_idx], next_state

    # Recursive call
    return solve_sungka_best_fit(
        next_state,
        path + [pit_idx],
        visited,
        depth + 1,
        max_depth
    )
    

def get_best_sungka_move(current_pits):
    """
    Evaluates all valid moves and selects the best one based on a 2D scoring table.
    Table structure: [Pit Index][Metric]
    """
    valid_pits = [i for i in range(g_pits) if current_pits[i] > 0]
    #print(f"valid_pits:{valid_pits}")
    if not valid_pits:
        return -1, None

    # 2D Table: Rows = Pits (0-4), Columns = [Points Gained, Bonus Flag, Survival Flag]
    # We initialize with -1 or 0.
    scoring_table = [-1] * g_pits
    max_score = num_pits+10
    for pit_idx in valid_pits:
        next_state, bonus, game_over = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)
        #print(f"next_state: {next_state}")

        if game_over:
            # Huge penalty for overshooting
            scoring_table[pit_idx] =-99
        else:
            #print(f"next_state[pit_idx] = {next_state[pit_idx]}, current_pits[pit_idx] = {current_pits[pit_idx]}")
            #points_gained = next_state[pit_idx] - current_pits[pit_idx]
            bonus_val = num_pits if bonus else 0  # Weight bonus turns heavily
            survival_val = 1 # It didn't crash

            distance = abs(g_pits - pit_idx)
            #print(f"pit_idx : {pit_idx} distance: {distance} current:{current_pits[pit_idx]}")
            if distance == current_pits[pit_idx] and distance!=g_pits:
                #print("should be here")
                scoring_table[pit_idx] = max_score
            elif distance == g_pits:
                scoring_table[pit_idx] = num_pits

            else:
                #print(f"points={points_gained} + {bonus_val} + {survival_val} = {points_gained + bonus_val + survival_val}")
                scoring_table[pit_idx] =  bonus_val + survival_val

    #print(f"current pit = {current_pits}")
    #print(f"Score table = {scoring_table}")
    # Selection Logic: Sum the metrics and find the max
    best_pit = -1
    best_pit2 =-1
    
    (best_val, best_pit), (best2_val, best_pit2) = get_top_two_with_indices(scoring_table)


    #print(f"best pit1: {best_pit}, best pit2: {best_pit2}, sum best fit1:{best_val}")
    if best_val<0 and best2_val<0:
        return -1,[]

    if best_val<0:
        best_pit = best_pit2
    else:
        if best_val< max_score and best_val>=0 and best2_val == best_val and best_pit2 < best_pit :
            best_pit = best_pit2

        if best_val< max_score and best_val>=0  and best2_val < max_score and best2_val>=0  and best_pit2 > best_pit :
            best_pit = best_pit2

        if best_val ==max_score and best2_val==max_score and best_pit< best_pit2:
            best_pit = best_pit2
        
        if best_val == max_score and best2_val< max_score and best2_val>=0 and best_pit2 > best_pit:
            best_pit=best_pit2
        #if best_val <30 and best2_val ==30 and best_pit2> best_pit:
        #    best_pit = best_pit2
    

    #print(f"best_pit: {best_pit}")
    return best_pit, scoring_table

def get_top_two_with_indices(arr):
    # (value, index)
    best = (-float('inf'), -1)
    best2 = (-float('inf'), -1)

    for idx, val in enumerate(arr):
        #print(f"idx: {idx}, score: {val}")

        if val >= best[0]:
            best2 = best      # Move old #1 to #2
            best = (val, idx) # Set new #1
        elif val >= best2[0]:
            best2 = (val, idx)
            
    return best, best2

def parse_json_file(filename):
    filepath = os.path.join(DATASET_DIR, filename)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    return data




results = [] 

if __name__ == "__main__":

    i =0# 1 for input array , 0 for input dataset
    
    if i==1:
        num_pits = 30
        g_pits = num_pits
        seeds = [19, 13, 30, 28, 2, 12, 24, 6, 1, 20, 10, 16, 20, 11, 11, 30, 22, 14, 1, 3, 16, 3, 7, 26, 18, 25, 22, 26, 6, 25, 0]

        board = SungkaBoard(num_pits=num_pits,seeds_per_pit = seeds )
        print("-" * 30)
        print(f"Board : {board.pits}")
        #print(f"Initial Board (Pits): {board.pits[:num_pits]}")
        print("Searching for optimal strategy...")
        path, last_state = solve_sungka_best_fit(board.pits)
        print(f"Optimal Result: {last_state[num_pits]} seeds in store.")
        print(f"Sequence of pit indices: {path}")
        print(f"Last State: {last_state}")
    else:
        tracemalloc.start()
        num_pits = 500# Reduced for faster calculation, change to 10 if needed
        DATASET_DIR = "dataset"
        data = parse_json_file("pit_"+str(num_pits)+".json")
        g_pits = num_pits
        print(f"Total arrays: {len(data)}")
        #print(f"First array: {data[0]}")

        # --- Execution ---
        start = time.perf_counter()

        tot_time=0

        for i, arr in enumerate(data):
            start = time.perf_counter()
            seeds = arr
            board = SungkaBoard(num_pits=num_pits,seeds_per_pit = seeds )
            print("-" * 30)
            print(f"Board {i}: {board.pits}")
            #print(f"Initial Board (Pits): {board.pits[:num_pits]}")
            print("Searching for optimal strategy...")
            path, last_state = solve_sungka_best_fit(board.pits)
            print(f"Optimal Result: {last_state[num_pits]} seeds in store.")
            print(f"Sequence of pit indices: {path}")
            print(f"Last State: {last_state}")
            end = time.perf_counter()
            elapsed =  (end - start)
            tot_time += elapsed
            print(f"Execution time: {end - start:.6f} seconds")
            results.append({
                "board_index": i,
                "initial_board": board.pits,
                "max_seeds": last_state[num_pits],
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

        output_file = "results/approx/approx_pit_"+ str(num_pits)+".json"

        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)