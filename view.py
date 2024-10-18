import pickle
import pprint

file_path = "q_table_1.pkl"
output_file = 'db_1.txt'

try:
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
except (FileNotFoundError, EOFError) as e:
    print(f"Error loading the pickle file: {e}")
    data = {}

with open(output_file, 'w') as f_out:
    pprint.pprint(data, stream=f_out)

file_path = "q_table_2.pkl"
output_file = 'db_2.txt'

try:
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
except (FileNotFoundError, EOFError) as e:
    print(f"Error loading the pickle file: {e}")
    data = {}

with open(output_file, 'w') as f_out:
    pprint.pprint(data, stream=f_out)