import pickle
import pprint

file_path = "q_table.pkl"
output_file = 'db.txt'

try:
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
except (FileNotFoundError, EOFError) as e:
    print(f"Error loading the pickle file: {e}")
    data = {}

with open(output_file, 'w') as f_out:
    pprint.pprint(data, stream=f_out)