import random
import json

motors = [1, 2, 3, 4, 5]
times_turn = []
shuffle_data = {}

for motor in range(len(motors)):

    times_turn.append(random.randint(1,5))
    shuffle_data[motor] = times_turn[motor]
     
with open("cube_shuffle.json", "w") as f:
                json.dump(shuffle_data, f, indent=4)