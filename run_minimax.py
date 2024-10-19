import os
import subprocess
import datetime
import my_go

PLAY_TIME = 100
# TA_AGENT = "random_player.py"
TA_AGENT = "weak_minimax.py"
# TA_AGENT = "my_player3.py"
PREFIX = "./init"
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

def cleanup():
    for filename in [INPUT_FILE, OUTPUT_FILE]:
        if os.path.exists(filename):
            os.remove(filename)

def play(black_cmd, white_cmd):
    cleanup()
    with open(os.path.join(PREFIX, INPUT_FILE), 'rb') as src:
        with open(INPUT_FILE, 'wb') as dst:
            dst.write(src.read())

    print("Start Playing...")

    moves = 0
    while True:
        print("Black makes move...")
        subprocess.run(black_cmd, shell=True, check=True)
        moves += 1

        # rst = subprocess.run(f"python3 ./host.py -m {moves} -v True", shell=True)
        # rst = subprocess.run(f"python3 ./host.py -m {moves}", shell=True)
        # rst = subprocess.run(f"python3 ./my_go.py -m {moves}", shell=True)
        rst, score = my_go.judge(moves)

        if rst != 0:
            break

        print("White makes move...")
        subprocess.run(white_cmd, shell=True, check=True)
        moves += 1

        # rst = subprocess.run(f"python3 ./host.py -m {moves} -v True", shell=True)
        # rst = subprocess.run(f"python3 ./host.py -m {moves}", shell=True)
        # rst = subprocess.run(f"python3 ./my_go.py -m {moves}", shell=True)
        rst, score = my_go.judge(moves)

        if rst != 0:
            break
    
    return rst

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
        print(f"=====Round {round}=====")
        print("Black: TA White: You")
        winner = play(ta_cmd, "python3 my_player3.py")

        if winner == 2:
            print('White (You) win!')
            white_win_time += 1
        elif winner == 0:
            print('Tie.')
            white_tie += 1
        else:
            print('White (You) lose.')

        print(f"=====Round {round + 1}=====")
        print("Black: You White: TA")
        winner = play("python3 my_player3.py", ta_cmd)

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