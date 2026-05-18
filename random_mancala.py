import random
import time


g_pits = 3
class SungkaBoard:
    def __init__(self, num_pits=g_pits, seeds_per_pit=None):
        self.num_pits = num_pits
        # Storehouse is at index 'num_pits' (the 101st slot)
        self.storehouse_idx = num_pits
        if seeds_per_pit:
            self.pits = seeds_per_pit
        else:
            #self.pits = [random.randint(1, g_pits) for _ in range(num_pits)] + [0]
            #self.pits = [25,3,24,19,10,17,21,1,22,15,6,2,2,6,22,3,16,18,24,12,14,20,7,21,12] + [0]
            #self.pits = [25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1] + [0]
            self.pits = [3,2,1] + [0]

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
            current_idx = (current_idx + 1) % (self.num_pits + 1)
            
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

def solve_sungka(current_pits, moves_left, path=[]):
    """Recursive backtracking to find the sequence of moves."""
    # Base Case: No moves left
    
    if moves_left == 0:
            print(f"---** path={path}")
            print(f"---- pit_idx={0} moves left={moves_left},store = {current_pits[5]} ")
            return path, current_pits[5] 

    # Try every possible pit that has seeds
    while True:
         pit_idx = random.choice([0, 1, 2, 3, 4])
         if current_pits[pit_idx] > 0:
            break
    
    #while current_pits[pit_idx] > 0
    #for pit_idx in range(5):
    #   if current_pits[pit_idx] > 0:
    #print(f"---** path1={path}")
    #print(f"---- pit_idx={pit_idx} moves left={moves_left}")
    next_state = SungkaBoard(5, current_pits[:6]).simulate_move(pit_idx)
    #print(f"next_state={next_state}")
    result1= solve_sungka(next_state, moves_left - 1, path + [pit_idx] )
    #print(f"---** result1={result1}")
    store1 = current_pits[5]
    #print(f"---** path2={path}")
    result2= solve_sungka(next_state, moves_left - 1, path + [pit_idx])
    #print(f"---** result2={result2}")
    store2 = current_pits[5]

    
    print(f"---< store1={store1} vs store2={store2} >")
    if result1 and result2:
        if store1>store2:
            return result1
        else:
            return result2
    return None


def solve_sungka_random(current_pits, moves, path=[]):
    # 1. Base Case: No moves left
    #if moves_left <= 0:
    #    return path, current_pits[5]

    # 2. Identify valid pits to start from
    valid_pits = [i for i in range(g_pits) if current_pits[i] > 0]
    
    # 3. Base Case: No seeds left in any playable pits
    if not valid_pits:
        return path, current_pits[g_pits], current_pits
    crypto_gen = random.SystemRandom()

    # Pick a random move
    pit_idx = crypto_gen.choice(valid_pits)
    #print(f"---** pit_idx={pit_idx}")

    # 4. Unpack the three values from your modified simulation
    # next_state (list), bonus (bool), game_over (bool)
    next_state, bonus, game_over = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)

    # 5. Handle Game Over (Overshot the storehouse)
    if game_over:
        # Return current path and a penalty or current score
        return path + [pit_idx], current_pits[g_pits], current_pits

    # 6. Handle Bonus Moves
    # If 'bonus' is True, the last stone landed in the storehouse.
    # We don't subtract from moves_left because the player gets another turn.
    if bonus:
        moves=moves+1  # Bonus turn!
        new_path = path + [pit_idx] # Mark as bonus move
    else:
        new_path = path + [pit_idx]

    return solve_sungka_random(next_state, moves, new_path)


def solve_sungka_wdrules(current_pits, moves, path=[]):
    # 1. Base Case: No moves left
    #if moves_left <= 0:
    #    return path, current_pits[5]

    # 2. Identify valid pits to start from
    valid_pits = [i for i in range(g_pits) if current_pits[i] > 0]
    
    # 3. Base Case: No seeds left in any playable pits
    if not valid_pits:
        return path, current_pits[g_pits]
    

    # Pick a random move
    pit_idx = choose_helper(current_pits)
    #print(f"---** pit_idx={pit_idx}")

    # 4. Unpack the three values from your modified simulation
    # next_state (list), bonus (bool), game_over (bool)
    next_state, bonus, game_over = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)

    # 5. Handle Game Over (Overshot the storehouse)
    if game_over:
        # Return current path and a penalty or current score
        return path + [f"{pit_idx}(X)"], current_pits[g_pits] 

    # 6. Handle Bonus Moves
    # If 'bonus' is True, the last stone landed in the storehouse.
    # We don't subtract from moves_left because the player gets another turn.
    if bonus:
        moves=moves+1  # Bonus turn!
        new_path = path + [f"{pit_idx}*"] # Mark as bonus move
    else:
        new_path = path + [pit_idx]

    return solve_sungka_wdrules(next_state, moves, new_path)


def choose_helper(current_pits):
    storehouse_idx = g_pits
    # Table: [Pit Index][Distance Score, Bonus Score, Overshoot Flag]
    scoring_table = [[0, 0, 0] for _ in range(g_pits)]
    print(f"current_pits: {current_pits}")
    valid_moves = []

    for i in range(g_pits):
        seeds = current_pits[i]
        if seeds == 0:
            continue
            
        distance_to_store = storehouse_idx - i
        
        # 1. Check for Overshoot (Game Over Rule)
        # If seeds > distance, it will pass the storehouse in the first lap
        if seeds > distance_to_store:
            scoring_table[i][2] = 1  # Mark as Overshoot
            continue 

        # 2. Check for Bonus Move (Perfect Match)
        if seeds == distance_to_store:
            scoring_table[i][1] = distance_to_store # High weight for extra turn
        else:
            scoring_table[i][1] = 0
        
        # 3. Distance Score (Prefer moves closer to the storehouse for efficiency)
        # Or prefer moves further away to 'sweep' more seeds—let's go with efficiency:
        #if scoring_table[i][1] == 0:
        scoring_table[i][0] = seeds 
        
        valid_moves.append(i)

    # Decision Making
    best_pit = -1
    closest_store = 99999
    #closest_store2 = 

    for i in valid_moves:
        # Ignore if it causes an overshoot
        if scoring_table[i][2] == 1:
            continue
            
        # Total = Seeds banked + Bonus Weight
        # total_score = scoring_table[i][0] + scoring_table[i][1]

        if scoring_table[i][1] !=0 and scoring_table[i][1] < closest_store:
            closest_store = scoring_table[i][1] 
            best_pit = i


    if best_pit==-1:
        for i in valid_moves:
            if scoring_table[i][2] == 1:
                continue
            if scoring_table[i][0] !=0 and scoring_table[i][0] < closest_store:
                closest_store = scoring_table[i][0] 
                best_pit = i




    print(f"best_pit : {best_pit}")
    return best_pit

def check_best_solution(initial_pits, best_path, expected_store):
    current_pits = initial_pits[:g_pits+1]  # copy

    for pit_idx in best_path:
        # Optional safety check
        if current_pits[pit_idx] == 0:
            return False  # invalid move sequence
        
        current_pits = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)

    return current_pits[g_pits] == expected_store


start = time.perf_counter()
# Setup the problem
board = SungkaBoard(num_pits=g_pits)
print(f"board: {board.pits}")
moves=0
best = (None, -1)
#path, score = solve_sungka_wdrules(board.pits, moves, [])
#print(f"path={path}, score={score}")
print("----------------")

for _ in range(100000):  # sampling
    path, score, last_state = solve_sungka_random(board.pits, moves, [])
    #print(f"path={path}, score={score}")
    if score > best[1]:
         best = (path, score, last_state)
print(f"best path = {best[0]} best score ={best[1]} last state = {best[2]}") 
end = time.perf_counter()
print(f"Execution time: {end - start:.6f} seconds")


'''
best = (None, -1)
for moves in range(10):
    for _ in range(10):  # sampling
        path, score = solve_sungka_random(board.pits, moves, [])
        if score > best[1]:
            best = (path, score)

    print(best)
    is_correct = check_best_solution(board.pits, best[0], best[1])
    print(is_correct)  # True if correct

'''