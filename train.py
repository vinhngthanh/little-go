import os
import subprocess
import datetime
import my_go
from my_qlearner import QLearner
PLAY_TIME = 10000
TA_AGENT = "random_player.py"
# TA_AGENT = "weak_minimax.py"
# TA_AGENT = "my_minimax.py"
PREFIX = "./init"
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

def cleanup():
    for filename in [INPUT_FILE, OUTPUT_FILE]:
        if os.path.exists(filename):
            os.remove(filename)

def play(black_cmd, white_cmd, white_agent = None, black_agent = None):
    cleanup()
    with open(os.path.join(PREFIX, INPUT_FILE), 'rb') as src:
        with open(INPUT_FILE, 'wb') as dst:
            dst.write(src.read())

    print("Start Playing...")

    moves = 0
    while True:
        print("Black makes move...")
        if black_agent:
            black_agent.execute()
        else:
            subprocess.run(black_cmd, shell=True, check=True)
        moves += 1

        # rst = subprocess.run(f"python3 ./host.py -m {moves} -v True", shell=True)
        # rst = subprocess.run(f"python3 ./host.py -m {moves}", shell=True)
        # rst = subprocess.run(f"python3 ./my_go.py -m {moves}", shell=True)
        rst, score = my_go.judge(moves)

        if rst != 0:
            break

        print("White makes move...")
        if white_agent:
            white_agent.execute()
        else:
            subprocess.run(white_cmd, shell=True, check=True)
        moves += 1

        # rst = subprocess.run(f"python3 ./host.py -m {moves} -v True", shell=True)
        # rst = subprocess.run(f"python3 ./host.py -m {moves}", shell=True)
        # rst = subprocess.run(f"python3 ./my_go.py -m {moves}", shell=True)
        rst, score = my_go.judge(moves)

        if rst != 0:
            break
    
    return rst, score

def main():
    print("")
    start_time = datetime.datetime.now()
    print(start_time)

    black_win_time = 0
    white_win_time = 0
    black_tie = 0
    white_tie = 0

    ta_cmd = f"python3 {TA_AGENT}"
    
    for round in range(1, PLAY_TIME + 1, 2):
        white_agent = QLearner(piece_type = 2, alpha = 0.7, gamma = 0.9, epsilon = 0.0, initial_value = 0.5)
        
        print(f"=====Round {round}=====")
        print("Black: TA White: You")
        winner, score = play(ta_cmd, "python3 my_player3.py", white_agent = white_agent)
        white_agent.learn(winner, score)

        if winner == 2:
            print('White (You) win!')
            white_win_time += 1
        elif winner == 0:
            print('Tie.')
            white_tie += 1
        else:
            print('White (You) lose.')

        black_agent = QLearner(piece_type = 1, alpha = 0.7, gamma = 0.9, epsilon = 0.0, initial_value = 0.5)

        print(f"=====Round {round + 1}=====")
        print("Black: You White: TA")
        winner, score = play("python3 my_player3.py", ta_cmd, black_agent = black_agent)
        black_agent.learn(winner, score)

        if winner == 1:
            print('Black (You) win!')
            black_win_time += 1
        elif winner == 0:
            print('Tie.')
            black_tie += 1
        else:
            print('Black (You) lose.')
        print()

        print("===== Wins =====")
        print(f"You play as Black Player | Win: {black_win_time} / {round // 2 + 1}")
        print(f"You play as White Player | Win: {white_win_time} / {round // 2 + 1}")
        print(f"Black win rate: {(black_win_time / (round // 2 + 1)):.2f}")
        print(f"WHite win rate: {(white_win_time / (round // 2 + 1)):.2f}")
        print(f"Win rate: {((black_win_time + white_win_time) / (round + 1)):.2f}")
        print()

    print("===== Summary =====")
    print(f"You play as Black Player | Win: {black_win_time} | Lose: {(PLAY_TIME // 2) - black_win_time - black_tie} | Tie: {black_tie}")
    print(f"You play as White Player | Win: {white_win_time} | Lose: {(PLAY_TIME // 2) - white_win_time - white_tie} | Tie: {white_tie}")

    cleanup()

    print("")
    print("Mission Completed.")
    end_time = datetime.datetime.now()
    print(end_time)
    total_runtime = end_time - start_time
    print(f"Total Runtime: {total_runtime}")

if __name__ == "__main__":
    main()