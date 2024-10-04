import random
import sys
from read import readInput
from write import writeOutput
from copy import deepcopy

from host import GO

class MyPlayer():
    def get_valid_placements(go, piece_type):
        N = go.size
        possible_placements = []

        for i in range(N):
            for j in range(N):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        return possible_placements
    
    def minimax(self, go, piece_type, max_depth, alpha, beta):
        placements = self.get_valid_placements(go, piece_type)
        best_moves = ()
        best_score = 0

        for placement in placements:
            prev_board = deepcopy(go.previous_board)
            go.previous_board = deepcopy(go.board)
            go.place_chess(placement[0], placement[1], piece_type)
            score = self.maximizing_player(go, max_depth, alpha, beta, 3 - piece_type)

            if score > best_score or not best_moves:
                best_score = score
                alpha = best_score
                best_moves = [placement]
            elif score == best_score:
                best_moves.append(placement)

            go.remove_certain_pieces(placement)
            go.previous_board = prev_board
        
        return best_moves

    def maximizing_player(go, max_depth, alpha, beta, piece_type):
        best = heuristic(curr_state, next_player)
        if max_depth == 0:
            return best

        curr_state_copy = copy.deepcopy(curr_state)

        for move in find_valid_moves(curr_state, prev_state, next_player):
            # update the next board state
            next_state = make_move(curr_state, move, next_player)
            # get the score from the minimizing player
            curr_score = -1 * min_play(next_state, curr_state_copy, max_depth-1, alpha, beta, 3-next_player)

            # check if we have to update best
            if curr_score > best:
                best = curr_score
            
            # update opponent's score from move
            opponent = -1 * best

            # check if prune and/or update alpha value
            if opponent < beta:
                return best
            if best > alpha:
                alpha = best
        
        return best
    
if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    max_depth = 2
    alpha = -1000000000
    beta = 1000000000
    action = player.minimax(go, piece_type, max_depth, alpha, beta)
    writeOutput(action)