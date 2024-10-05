import random
import sys
from read import readInput
from write import writeOutput
from copy import deepcopy
from host import GO

class MyPlayer:
    def __init__(self, go, piece_type):
        self.go = go
        self.piece_type = piece_type

    def get_valid_placements(self):
        N = self.go.size
        possible_placements = []

        for i in range(N):
            for j in range(N):
                if self.go.valid_place_check(i, j, self.piece_type, test_check=True):
                    possible_placements.append((i, j))

        return possible_placements
    
    def minimax(self, max_depth, alpha, beta):
        placements = self.get_valid_placements()
        best_moves = []
        best_score = -1000

        for placement in placements:
            prev_board = deepcopy(self.go.previous_board)
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], self.piece_type)

            score = self.minimizing_player(max_depth, alpha, beta, self.piece_type)

            if score > best_score:
                best_score = score
                alpha = best_score
                best_moves = [placement]
            elif score == best_score:
                best_moves.append(placement)

            self.go.remove_certain_pieces([placement])
            self.go.previous_board = prev_board
        
        return best_moves

    def maximizing_player(self, max_depth, alpha, beta, piece_type):
        placements = self.get_valid_placements()
        best_score = -1000

        if self.go.game_end(piece_type) or max_depth == 0:
            if self.go.judge_winner() == self.piece_type:
                return 1
            elif self.go.judge_winner() == 3 - self.piece_type:
                return -1
            else:
                return 0

        for placement in placements:
            prev_board = deepcopy(self.go.previous_board)
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)

            curr_score = self.minimizing_player(max_depth - 1, alpha, beta, 3 - piece_type)
            alpha = max(alpha, curr_score)
            best_score = max(best_score, curr_score)
            
            self.go.remove_certain_pieces([placement])
            self.go.previous_board = prev_board

            if beta <= alpha:
                break
        
        return best_score

    def minimizing_player(self, max_depth, alpha, beta, piece_type):
        placements = self.get_valid_placements()
        best_score = 1000

        if self.go.game_end(piece_type) or max_depth == 0:
            if self.go.judge_winner() == self.piece_type:
                return 1
            elif self.go.judge_winner() == 3 - self.piece_type:
                return -1
            else:
                return 0

        for placement in placements:
            prev_board = deepcopy(self.go.previous_board)
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)

            curr_score = self.maximizing_player(max_depth - 1, alpha, beta, self.piece_type)
            beta = min(beta, curr_score)
            best_score = min(best_score, curr_score)
            
            self.go.remove_certain_pieces([placement])
            self.go.previous_board = prev_board

            if beta <= alpha:
                break
        
        return best_score

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer(go, piece_type)
    max_depth = 3
    alpha = -1000
    beta = 1000
    action = player.minimax(max_depth, alpha, beta)
    rand_action = random.choice(action)
    writeOutput(rand_action)