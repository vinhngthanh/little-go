import random
import sys
from read import readInput
from write import writeOutput
from copy import deepcopy
from my_go import GO

class MyPlayer:
    def __init__(self, go, my_piece_type):
        self.go = go
        self.my_piece_type = my_piece_type

    def get_valid_placements(self, piece_type):
        N = self.go.size
        possible_placements = []

        for i in range(N):
            for j in range(N):
                if self.go.valid_place_check(i, j, piece_type):
                    possible_placements.append((i, j))

        return possible_placements
    
    def evaluate_board(self):
        my_score = 0
        opp_score = 0
        my_liberty = 0
        opp_liberty = 0
        my_territory = 0
        opp_territory = 0
        my_capture_potential = 0
        opp_capture_potential = 0

        for i in range(5):
            for j in range(5):
                if self.go.board[i][j] == self.my_piece_type:
                    my_score += 1
                    my_liberty += self.go.count_liberty(i, j)
                    
                    if self.go.is_surrounded(i, j, 3 - self.my_piece_type):
                        my_capture_potential += 1

                elif self.go.board[i][j] == 3 - self.my_piece_type:
                    opp_score += 1
                    opp_liberty += self.go.count_liberty(i, j)

                    if self.go.is_surrounded(i, j, self.my_piece_type):
                        opp_capture_potential += 1

        for i in range(5):
            for j in range(5):
                if self.go.board[i][j] == 0:
                    adjacent_stones = self.go.detect_neighbor(i, j)
                    if all(s == self.my_piece_type for s in adjacent_stones if s != 0):
                        my_territory += 1
                    elif all(s == 3 - self.my_piece_type for s in adjacent_stones if s != 0):
                        opp_territory += 1

        my_total_score = (
            my_score + my_liberty + my_territory +
            (my_capture_potential * 5)
        )
        opp_total_score = (
            opp_score + opp_liberty + opp_territory +
            (opp_capture_potential * 5)
        )

        komi = 2.5 if self.my_piece_type == 1 else -2.5

        return my_total_score - opp_total_score + komi


    def minimax(self, max_depth, alpha, beta):
        best_moves = []
        best_score = -10000
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(self.my_piece_type)

        self.go.visualize_board()

        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], self.my_piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - self.my_piece_type)

            # self.go.visualize_board()

            score = self.minimizing_player(max_depth, alpha, beta, 3 - self.my_piece_type)

            if score > best_score:
                best_score = score
                alpha = best_score
                best_moves = [placement]
            elif score == best_score:
                best_moves.append(placement)

            self.go = copy_go.copy_board()
        
        # print(best_score)
        # print(best_moves)
        return best_moves

    def maximizing_player(self, max_depth, alpha, beta, piece_type):
        best_score = self.evaluate_board()

        if self.go.game_end(piece_type) or max_depth == 0:
            # print(self.evaluate_board())        
            return best_score
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(piece_type)
        
        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - piece_type)

            # self.go.visualize_board()

            curr_score = self.minimizing_player(max_depth - 1, alpha, beta, 3 - piece_type)
            alpha = max(alpha, curr_score)
            best_score = max(best_score, curr_score)
            
            self.go = copy_go.copy_board()

            if beta <= alpha:
                break

        return best_score

    def minimizing_player(self, max_depth, alpha, beta, piece_type):
        best_score = self.evaluate_board()

        if self.go.game_end(piece_type) or max_depth == 0:
            # print(self.evaluate_board())
            return best_score
        
        copy_go = self.go.copy_board()
        placements = self.get_valid_placements(piece_type)
        
        for placement in placements:
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(placement[0], placement[1], piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - piece_type)

            # self.go.visualize_board()

            curr_score = self.maximizing_player(max_depth - 1, alpha, beta, 3 - piece_type)
            beta = min(beta, curr_score)
            best_score = min(best_score, curr_score)
            
            self.go = copy_go.copy_board()

            if beta <= alpha:
                break
        
        return best_score
    
    def choose_statistical_best(self, best_moves):
        best_scores = []
        
        copy_go = self.go.copy_board()

        for move in best_moves:
            i, j = move
            
            self.go.previous_board = deepcopy(self.go.board)
            self.go.place_chess(i, j, self.my_piece_type)
            self.go.died_pieces = self.go.remove_died_pieces(3 - self.my_piece_type)
            
            liberty_score = self.go.count_liberty(i, j)
            capture_potential = len(self.go.died_pieces)
            
            potential_territory = 0
            adjacent_stones = self.go.detect_neighbor(i, j)
            if all(s == self.my_piece_type for s in adjacent_stones if s != 0):
                potential_territory += 1
            
            position_score = 0
            center_positions = [(2, 2), (1, 2), (2, 1), (2, 3), (3, 2)]
            if (i, j) in center_positions:
                position_score += 1
            
            move_score = (liberty_score * 2) + (capture_potential * 3) + (potential_territory * 4) + (position_score * 1.5)
            best_scores.append((move_score, move))
            
            self.go = copy_go.copy_board()
        
        best_scores.sort(reverse=True, key=lambda x: x[0])
        
        return best_scores[0][1] if best_scores else None


if __name__ == "__main__":
    N = 5
    my_piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(my_piece_type, previous_board, board)
    player = MyPlayer(go, my_piece_type)
    max_depth = 2
    alpha = -10000
    beta = 10000

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
            best_action = player.choose_statistical_best(action)

    # print(best_action)
    writeOutput(best_action)