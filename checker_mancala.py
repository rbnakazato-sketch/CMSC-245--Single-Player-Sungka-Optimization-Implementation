import random

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
            self.pits = [8,7,6,5,4,3,2,1] + [0]
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

        while hand > 0:
            #current_idx = (current_idx + 1) % (self.num_pits + 1)
            current_idx += 1
            if current_idx > g_pits:
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

def check_best_solution(initial_pits, best_path, expected_store):
    current_pits = initial_pits

    
    for pit_idx in best_path:
        # Optional safety check
        #print(f"pit_idx = {pit_idx}, type: {type(pit_idx)} ")
        print(f"current_pits = {current_pits},  pit_idx= { pit_idx}")
        if current_pits[pit_idx] == 0:
            return False  # invalid move sequence
        current_pits = SungkaBoard(g_pits, current_pits).simulate_move(pit_idx)[0]
        print(f"current_pits = {current_pits}")

    return current_pits[g_pits] == expected_store

g_pits = 30
b_state =[2, 6, 18, 2, 12, 24, 16, 20, 26, 15, 3, 9, 5, 11, 17, 11, 29, 13, 7, 13, 6, 9, 24, 23, 29, 12, 18, 2, 25, 13, 0]







board = SungkaBoard(num_pits=g_pits, seeds_per_pit =b_state )
print(f"board: {board.pits}")
path =[21, 27, 17, 3, 15, 2, 1, 20, 18]






score = 9
is_correct = check_best_solution(board.pits, path, score)
if is_correct:
    print("Moves Valid")
else:
    print("Invalid Moves")