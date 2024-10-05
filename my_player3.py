import random
import sys
from read import readInput
from write import writeOutput
from copy import deepcopy
from host import GO

class MyPlayer:
    def __init__(self, go, my_piece_type):
        self.go = go
        self.my_piece_type = my_piece_type

    def get_valid_placements(self, piece_type):
        N = self.go.size
        possible_placements = []

        for i in range(N):
            for j in range(N):
                if self.go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        return possible_placements
    
    def minimax(self, max_depth, alpha, beta):
        best_moves = []
        best_score = -1000
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(self.my_piece_type)

        self.go.visualize_board()

        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], self.my_piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - self.my_piece_type)

            self.go.visualize_board()

            score = self.minimizing_player(max_depth, alpha, beta, 3 - self.my_piece_type)

            if score > best_score:
                best_score = score
                alpha = best_score
                best_moves = [placement]
            elif score == best_score:
                best_moves.append(placement)

            self.go = copy_go.copy_board()
        
        return best_moves

    def maximizing_player(self, max_depth, alpha, beta, piece_type):
        if self.go.game_end(piece_type) or max_depth == 0:
            print("return")
            return self.evaluate_board()
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(piece_type)
        best_score = -1000

        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - piece_type)

            self.go.visualize_board()

            curr_score = self.minimizing_player(max_depth - 1, alpha, beta, 3 - piece_type)
            alpha = max(alpha, curr_score)
            best_score = max(best_score, curr_score)
            
            self.go = copy_go.copy_board()

            if beta <= alpha:
                break
        
        return best_score

    def minimizing_player(self, max_depth, alpha, beta, piece_type):
        if self.go.game_end(piece_type) or max_depth == 0:
            print("return")
            return self.evaluate_board()
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(piece_type)
        best_score = 1000
        
        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - piece_type)

            self.go.visualize_board()

            curr_score = self.maximizing_player(max_depth - 1, alpha, beta, 3 - piece_type)
            beta = min(beta, curr_score)
            best_score = min(best_score, curr_score)
            
            self.go = copy_go.copy_board()

            if beta <= alpha:
                break
        
        return best_score
    
    def evaluate_board(self):
        if self.go.judge_winner() == self.my_piece_type:
            return 1
        elif self.go.judge_winner() == 3 - self.my_piece_type:
            return -1
        return 0

if __name__ == "__main__":
    N = 5
    my_piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(my_piece_type, previous_board, board)
    player = MyPlayer(go, my_piece_type)
    max_depth = 5
    alpha = -1000
    beta = 1000

    pieces = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] != 0:
                pieces += 1
    mid_empty = False
    if board[2][2] == 0:
        mid_empty = True

    best_action = "PASS"
    if (pieces == 0 and my_piece_type == 1) or (pieces == 1 and my_piece_type == 2 and mid_empty):
        best_action = (2, 2)
    else:
        action = player.minimax(max_depth, alpha, beta)
        if(action):
            best_action = random.choice(action)

    writeOutput(best_action)