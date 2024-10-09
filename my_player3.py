import random
import numpy as np
import pickle
from read import readInput
from write import writeOutput
from host import GO

WIN_REWARD = 1.0
DRAW_REWARD = 0.5
LOSS_REWARD = 0.0
QFILE = "q_table.pkl"

class QLearner:
    def __init__(self, piece_type, alpha, gamma, epsilon, initial_value, q_file = QFILE):
        self.piece_type = piece_type
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_file = q_file
        self.q_values = self.load_q_values(QFILE)
        self.history_states = []
        self.initial_value = initial_value

    def get_input(self, go, piece_type):    
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        action = "PASS"
        if not possible_placements:
            return action
        
        if random.uniform(0, 1) < self.epsilon:
            action = self.select_best_move(go, possible_placements, True)
        else:
            action = self.select_best_move(go, possible_placements, False)
        
        return action

    def select_best_move(self, go, possible_placements, mutate):
        canonical_board, transformation = self.get_canonical_board(go.board)
        transformed_state = self.encode_state(canonical_board)
        q_values = self.Q(transformed_state)

        best_move = None
        if mutate:
            move = random.choice(possible_placements)
            best_move = self.transform_move(move, transformation)
        else:
            max_q_value = -np.inf
            for move in possible_placements:
                row, col = self.transform_move(move, transformation)
                if q_values[row][col] > max_q_value:
                    max_q_value = q_values[row][col]
                    best_move = (row, col)

        self.record_move(transformed_state, best_move)
        reverted_move = self.revert_move(best_move, transformation)
        return reverted_move

    def Q(self, state):
        if state not in self.q_values:
            q_val = np.zeros((5, 5))
            q_val.fill(self.initial_value)
            self.q_values[state] = q_val
        return self.q_values[state]

    def encode_state(self, board):
        return tuple(tuple(int(cell) for cell in row) for row in board)

    def generate_transformations(self, board):
        transformations = []
        
        transformations.append(board)
        
        for _ in range(3):
            board = np.rot90(board)
            transformations.append(board)
        
        transformations.extend([np.fliplr(b) for b in transformations])
        transformations.extend([np.flipud(b) for b in transformations])
        
        return transformations
    
    def get_canonical_board(self, board):
        transformations = self.generate_transformations(board)
        transformations_tuples = [tuple(map(tuple, b)) for b in transformations]
        
        canonical_board_tuple = min(transformations_tuples, key=lambda x: self.encode_state(x))
        
        transformation_index = None
        for idx, transformed_board in enumerate(transformations_tuples):
            if transformed_board == canonical_board_tuple:
                transformation_index = idx
                break

        canonical_board = transformations[transformation_index]

        return canonical_board, transformation_index
        
    def revert_move(self, move, transformation):
        reverted_move = (int(move[0]), int(move[1]))

        if transformation == 0:
            pass
        elif transformation == 1:
            reverted_move = (move[1], 4 - move[0])
        elif transformation == 2:
            reverted_move = (4 - move[0], 4 - move[1])
        elif transformation == 3:
            reverted_move = (4 - move[1], move[0])
        elif transformation == 4:
            reverted_move = (move[0], 4 - move[1])
        elif transformation == 5:
            reverted_move = (4 - move[0], move[1])

        return reverted_move
    
    def transform_move(self, move, transformation):
        transformed_move = (int(move[0]), int(move[1]))

        if transformation == 0:
            pass
        elif transformation == 1:
            transformed_move = (4 - move[1], move[0])
        elif transformation == 2:
            transformed_move = (4 - move[0], 4 - move[1])
        elif transformation == 3:
            transformed_move = (move[1], 4 - move[0])
        elif transformation == 4:
            transformed_move = (move[0], 4 - move[1])
        elif transformation == 5:
            transformed_move = (4 - move[0], move[1])

        return transformed_move

    def learn(self, result):
        if result == self.piece_type:
            reward = WIN_REWARD
        elif result == 0:
            reward = DRAW_REWARD
        else:
            reward = LOSS_REWARD
        
        self.history_states.reverse()
        max_q_value = -1.0
        
        for state, move in self.history_states:
            q = self.Q(state)
            if max_q_value < 0:
                q[move[0]][move[1]] = reward
            else:
                q[move[0]][move[1]] = (1 - self.alpha) * q[move[0]][move[1]] + self.alpha * self.gamma * max_q_value
            max_q_value = np.max(q)
        
        self.save_q_values()
        self.history_states = []

    def record_move(self, state, move):
        self.history_states.append((state, move))

    def save_q_values(self):
        with open(self.q_file, 'wb') as f:
            pickle.dump(self.q_values, f)
    
    def load_q_values(self, q_file):
        try:
            with open(q_file, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return {}
        
    def execute(self):
        N = 5
        piece_type, previous_board, board = readInput(N)
        go = GO(N)
        go.set_board(piece_type, previous_board, board)

        pieces = 0
        for i in range(5):
            for j in range(5):
                if go.board[i][j] != 0:
                    pieces += 1

        action = "PASS"
        if pieces == 0 and self.piece_type == 1:
            action = (2, 2)
        else:
            action = self.get_input(go, self.piece_type)             
        writeOutput(action)

if __name__ == "__main__":
    N = 5
    alpha = 0.7
    gamma = 0.9
    epsilon = 0
    # epsilon = 0.1
    initial_value = 0.5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = QLearner(piece_type, alpha, gamma, epsilon, initial_value)
    action = player.get_input(go, piece_type)
    writeOutput(action)
