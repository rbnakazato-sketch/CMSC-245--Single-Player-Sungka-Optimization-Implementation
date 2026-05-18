import json
import random

def generate_file(filename, num_arrays, array_size):
    data = []
    
    for _ in range(num_arrays):
        # First (array_size - 1) elements are random from 1 to (array_size - 1)
        arr = [random.randint(1, array_size - 1) for _ in range(array_size - 1)]
        
        # Last element is always 0
        arr.append(0)
        
        data.append(arr)
    
    # Save to JSON file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# Generate the 5 files
generate_file("pit_500.json", 100, 501)   # 7 random + 0
#generate_file("pit_15.json", 100, 16)  # 15 random + 0
#generate_file("pit_30.json", 100, 31)  # 30 random + 0
#generate_file("pit_60.json", 100, 61)  # 60 random + 0
#generate_file("pit_120.json", 100, 121)  # 120 random + 0