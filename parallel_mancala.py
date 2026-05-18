import random
import time
import multiprocessing as mp
import json
import os
import tracemalloc


num_pits = 8

class SungkaBoard:
    def __init__(self, num_pits, seeds_per_pit=None):
        self.num_pits = num_pits
        self.storehouse_idx = num_pits
        if seeds_per_pit is not None:
            # seeds_per_pit should be just the pits; we add the storehouse [0]
            self.pits = list(seeds_per_pit) + [0]
        else:
            #self.pits = [random.randint(1, 10) for _ in range(num_pits)] + [0]
            self.pits = [8,7,6,5,4,3,2,1] + [0]

    '''def simulate_move(self, start_pit_idx):
        """
        Simulates move with no wrap-around. 
        Returns (new_state, can_continue) or (None, False) if overshoot.
        """
        temp_pits = list(self.pits)
        hand = temp_pits[start_pit_idx]
        
        # RULE: Cannot pick an empty pit
        if hand == 0:
            return None, False
            
        # RULE: NO OVERSHOOT
        if start_pit_idx + hand > self.storehouse_idx:
            print("Overshoot!")
            return None, False

        temp_pits[start_pit_idx] = 0
        current_idx = start_pit_idx
        
        # Sowing logic (Linear)
        while hand > 0:
            current_idx += 1
            temp_pits[current_idx] += 1
            hand -= 1
            
        # Check landing condition for additional move
        can_continue = False
        if current_idx == self.storehouse_idx:
            # RULE: Land in home store = additional move
            can_continue = True
        elif temp_pits[current_idx] > 1:
            # RULE: Land in non-empty pit = additional move
            can_continue = True
        # Else: Landed in empty pit = Game Over (can_continue remains False)

        if can_continue== False:
            print("Game Over")  
        return temp_pits, can_continue'''


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

        while hand > 0:
            #current_idx = (current_idx + 1) % (self.num_pits + 1)
            current_idx += 1
            if current_idx > num_pits:
                current_idx = 0
            
            # RULE: Check for overshoot/game over at the storehouse
            if current_idx == self.storehouse_idx:
                if hand > 1:
                    #print("Game Over: Overshot the storehouse!")
                    game_over = True
                    # Optional: You might want to return a specific 'Lose' state here
                    return temp_pits, False, True 
            
            # Sow the seed
            temp_pits[current_idx] += 1
            hand -= 1

            # RULE: Multi-lap logic (last seed in non-empty pit)
            # We only do this if it's NOT the storehouse
            if hand == 0 and current_idx != self.storehouse_idx and temp_pits[current_idx] > 1:
                hand = temp_pits[current_idx]
                temp_pits[current_idx] = 0
                
        # RULE: Check if the last stone landed in the storehouse
        if current_idx == self.storehouse_idx:
            can_move_again = True

        return temp_pits, can_move_again, game_over
    
import multiprocessing as mp

def worker_task(args):
    pit_idx, current_board_state, num_pits = args

    if current_board_state[pit_idx] == 0:
        return None

    board_obj = SungkaBoard(num_pits, current_board_state[:num_pits])
    board_obj.pits = list(current_board_state)

    next_state, can_continue, game_over = board_obj.simulate_move(pit_idx)

    if next_state is None:
        return None

    if can_continue:
        score, path, final_state = solve_sungka(next_state, memo={})
    else:
        score = next_state[num_pits]
        path = []
        final_state = next_state

    return (score, [pit_idx] + path, final_state)


def solve_sungka_parallel(current_board_state):
    num_pits = len(current_board_state) - 1

    tasks = [
        (pit_idx, current_board_state, num_pits)
        for pit_idx in range(num_pits)
    ]

    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(worker_task, tasks)

    best_score = current_board_state[num_pits]
    best_path = []
    best_final_state = current_board_state

    for result in results:
        if result is None:
            continue

        score, path, final_state = result

        if score > best_score:
            best_score = score
            best_path = path
            best_final_state = final_state

    return best_score, best_path, best_final_state


def solve_sungka(current_board_state, memo=None):
    if memo is None:
        memo = {}

    num_pits = len(current_board_state) - 1
    state_key = tuple(current_board_state)

    # 🔁 Memo check
    if state_key in memo:
        return memo[state_key]

    best_score = current_board_state[num_pits]
    best_path = []
    best_final_state = current_board_state  # default: no move

    for pit_idx in range(num_pits):
        if current_board_state[pit_idx] > 0:
            board_obj = SungkaBoard(num_pits, current_board_state[:num_pits])
            board_obj.pits = list(current_board_state)

            next_state, can_continue, game_over = board_obj.simulate_move(pit_idx)

            if next_state is not None:
                if can_continue:
                    score, sub_path, final_state = solve_sungka(next_state, memo)
                else:
                    score = next_state[num_pits]
                    sub_path = []
                    final_state = next_state  

                if score > best_score:
                    best_score = score
                    best_path = [pit_idx] + sub_path
                    best_final_state = final_state 
    # 💾 Store all three in memo
    memo[state_key] = (best_score, best_path, best_final_state)
    return memo[state_key]


def parse_json_file(filename):
    filepath = os.path.join(DATASET_DIR, filename)
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    num_pits = 500# Reduced for faster calculation, change to 10 if needed
    DATASET_DIR = "dataset"
    data = parse_json_file("pit_"+str(num_pits)+".json")
    
    print(f"Total arrays: {len(data)}")
    #print(f"First array: {data[0]}")

    # --- Execution ---
    start = time.perf_counter()
    tracemalloc.start()

    results = [] 
    tot_time=0
    for i, arr in enumerate(data):
        start = time.perf_counter()
        seeds = arr[:-1]
        board = SungkaBoard(num_pits=num_pits,seeds_per_pit = seeds )
        print("-" * 30)
        print(f"Board {i}: {board.pits}")
        #print(f"Initial Board (Pits): {board.pits[:num_pits]}")
        print("Searching for optimal strategy...")
        max_seeds, best_sequence, last_state = solve_sungka(board.pits)
        print(f"Optimal Result: {max_seeds} seeds in store.")
        print(f"Sequence of pit indices: {best_sequence}")
        print(f"Last State: {last_state}")
        end = time.perf_counter()
        elapsed = (end - start)
        tot_time += elapsed
        print(f"Execution time: {end - start:.6f} seconds")
        results.append({
            "board_index": i,
            "initial_board": board.pits,
            "max_seeds": max_seeds,
            "best_sequence": best_sequence,
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

    output_file = "results/pdp/results_pit_"+ str(num_pits) +".json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)