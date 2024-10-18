import random
import numpy as np
import pickle
from read import readInput
from write import writeOutput
from host import GO

WIN_REWARD = 1.0
DRAW_REWARD = 0.5
LOSS_REWARD = 0.0
QFILE_1 = "q_table_1.pkl"
QFILE_2= "q_table_2.pkl"

class QLearner:
    def __init__(self, piece_type, alpha, gamma, epsilon, initial_value):
        self.piece_type = piece_type
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_file = None
        self.q_values = None
        if self.piece_type == 1:
            self.q_file = QFILE_1
            self.q_values = self.load_q_values(QFILE_1)
        else:
            self.q_file = QFILE_2
            self.q_values = self.load_q_values(QFILE_2)
        self.history_states = []
        self.initial_value = initial_value

    def get_input(self, go):    
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, self.piece_type, test_check=True):
                    possible_placements.append((i, j))
        
        if random.uniform(0, 1) < self.epsilon:
            action = self.select_best_move(go, possible_placements, True)
        else:
            action = self.select_best_move(go, possible_placements, False)
        
        return action

    def select_best_move(self, go, possible_placements, mutate):
        canonical_board, transformation = self.get_canonical_board(go.board)
        transformed_state = self.encode_state_type(canonical_board)
        q_values, pass_value = self.Q(transformed_state)

        if not possible_placements:
            self.record_move(transformed_state, "PASS")
            return "PASS"

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
            if pass_value > max_q_value:
                best_move = "PASS"

        if best_move != "PASS":
            reverted_move = self.revert_move(best_move, transformation)
            self.record_move(transformed_state, best_move)
            return reverted_move
        else:
            self.record_move(transformed_state, best_move)
            return "PASS"

    def Q(self, state):
        if state not in self.q_values:
            q_val = np.zeros((5, 5))
            q_val.fill(self.initial_value)
            pass_value = float(self.initial_value)
            self.q_values[state] = (q_val, pass_value)
        return self.q_values[state]

    def encode_state(self, board):
        return tuple(tuple(int(cell) for cell in row) for row in board)
    
    def encode_state_type(self, board):
        encoded_board = tuple(tuple(int(cell) for cell in row) for row in board)
        return (encoded_board, self.piece_type)

    def generate_transformations(self, board):
        transformations = []
        
        transformations.append(board)
        
        for _ in range(3):
            board = np.rot90(board)
            transformations.append(board)

        transformations.extend([np.fliplr(b) for b in transformations])
        transformations.extend([np.flipud(b) for b in transformations])
        # print(transformations)
        return transformations
    
    def get_canonical_board(self, board):
        transformations = self.generate_transformations(board)
        # transformations_tuples = [tuple(map(tuple, b)) for b in transformations]
        # canonical_board_tuple = min(transformations_tuples, key=lambda x: self.encode_state(x))
        transformations_tuples = [self.encode_state(b) for b in transformations]
        canonical_board_tuple = min(transformations_tuples)

        transformation_index = None
        for idx, transformed_board in enumerate(transformations_tuples):
            if transformed_board == canonical_board_tuple:
                transformation_index = idx
                break

        canonical_board = transformations[transformation_index]

        return canonical_board, transformation_index
    
    def revert_move(self, move, transformation):
        reverted_move = (int(move[0]), int(move[1]))

        if transformation == 0:  # No transformation
            pass
        elif transformation == 1:  # 90 degrees clockwise
            reverted_move = (move[1], 4 - move[0])
        elif transformation == 2:  # 180 degrees clockwise
            reverted_move = (4 - move[0], 4 - move[1])
        elif transformation == 3:  # 270 degrees clockwise
            reverted_move = (4 - move[1], move[0])

        elif transformation == 4:  # Horizontal flip
            reverted_move = (move[0], 4 - move[1])
        elif transformation == 5:  # Horizontal flip + 90 degrees clockwise
            reverted_move = (4 - move[1], 4 - move[0])
        elif transformation == 6:  # Horizontal flip + 180 degrees clockwise
            reverted_move = (4 - move[0], move[1])
        elif transformation == 7:  # Horizontal flip + 270 degrees clockwise
            reverted_move = (move[1], move[0])

        elif transformation == 8:  # Vertical flip
            reverted_move = (4 - move[0], move[1])
        elif transformation == 9:  # Vertical flip + 90 degrees clockwise
            reverted_move = (move[1], move[0])
        elif transformation == 10:  # Vertical flip + 180 degrees clockwise
            reverted_move = (move[0], 4 - move[1])
        elif transformation == 11:  # Vertical flip + 270 degrees clockwise
            reverted_move = (4 - move[1], 4 - move[0])

        elif transformation == 12:  # Vertical flip + Horizontal flip
            reverted_move = (4 - move[0], 4 - move[1])
        elif transformation == 13:  # Vertical flip + Horizontal flip + 90 degrees clockwise
            reverted_move = (4 - move[1], move[0])
        elif transformation == 14:  # Vertical flip + Horizontal flip + 180 degrees clockwise
            reverted_move = (move[0], move[1])
        elif transformation == 15:  # Vertical flip + Horizontal flip + 270 degrees clockwise
            reverted_move = (move[1], 4 - move[0])

        return reverted_move

    def transform_move(self, move, transformation):
        transformed_move = (int(move[0]), int(move[1]))

        if transformation == 0:  # No transformation
            pass
        elif transformation == 1:  # 90 degrees anticlockwise
            transformed_move = (4 - move[1], move[0])
        elif transformation == 2:  # 180 degrees anticlockwise
            transformed_move = (4 - move[0], 4 - move[1])
        elif transformation == 3:  # 270 degrees anticlockwise
            transformed_move = (move[1], 4 - move[0])

        elif transformation == 4:  # Horizontal flip
            transformed_move = (move[0], 4 - move[1])
        elif transformation == 5:  # 90 degrees anticlockwise + Horizontal flip
            transformed_move = (4 - move[1], 4 - move[0])
        elif transformation == 6:  # 180 degrees anticlockwise + Horizontal flip
            transformed_move = (4 - move[0], move[1])
        elif transformation == 7:  # 270 degrees anticlockwise + Horizontal flip
            transformed_move = (move[1], move[0])

        elif transformation == 8:  # Vertical flip
            transformed_move = (4 - move[0], move[1])
        elif transformation == 9:  # 90 degrees anticlockwise + Vertical flip
            transformed_move = (move[1], move[0])
        elif transformation == 10:  # 180 degrees anticlockwise + Vertical flip
            transformed_move = (move[0], 4 - move[1])
        elif transformation == 11:  # 270 degrees anticlockwise + Vertical flip
            transformed_move = (4 - move[1], 4 - move[0])

        elif transformation == 12:  # Horizontal flip + Vertical flip
            transformed_move = (4 - move[0], 4 - move[1])
        elif transformation == 13:  # 90 degrees anticlockwise + Horizontal flip + Vertical flip
            transformed_move = (move[1], 4 - move[0])
        elif transformation == 14:  # 180 degrees anticlockwise + Horizontal flip + Vertical flip
            transformed_move = (move[0], move[1])
        elif transformation == 15:  # 270 degrees anticlockwise + Horizontal flip + Vertical flip
            transformed_move = (4 - move[1], move[0])

        return transformed_move


    def learn(self, result, score):
        if self.piece_type == 1:
            reward = -score - 2.5
        else:
            reward = score + 2.5
        
        self.history_states.reverse()
        max_q_value = -np.inf
        
        for state, move in self.history_states:
            q_values, pass_value = self.Q(state)
            if move == "PASS":
                if max_q_value < 0:
                    pass_value = reward
                else:
                    pass_value = (1 - self.alpha) * pass_value + self.alpha * self.gamma * max_q_value
                max_q_value = max(max_q_value, float(pass_value))
            else:
                if max_q_value < 0:
                    q_values[move[0]][move[1]] = float(reward)
                else:
                    q_values[move[0]][move[1]] = float((1 - self.alpha) * q_values[move[0]][move[1]] + self.alpha * self.gamma * max_q_value)
                # max_q_value = np.max(q)
                max_q_value = max(max_q_value, q_values[move[0]][move[1]])

            self.q_values[state] = (q_values, float(pass_value))
        
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
            action = self.get_input(go)                 
        writeOutput(action)

if __name__ == "__main__":
    N = 5
    alpha = 0.7
    gamma = 0.9
    # epsilon = 0
    epsilon = 0.3
    initial_value = 0.5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = QLearner(piece_type, alpha, gamma, epsilon, initial_value)

    pieces = 0
    for i in range(5):
        for j in range(5):
            if go.board[i][j] != 0:
                pieces += 1

    action = "PASS"
    if pieces == 0 and piece_type == 1:
        action = (2, 2)
    else:
        action = player.get_input(go, piece_type)             

    writeOutput(action)
