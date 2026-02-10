#main.py
import json
from modules.graph import PolyvilleMap
from modules.scheduler import Scheduler
from modules.sensor_analysis import detect_biased_sensor # IMPORT THIS

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def main():
    try:
        map_data = load_json('public_map.json')
        sensor_data = load_json('sensor_data.json')
        obj_data = load_json('objectives.json')
    except FileNotFoundError:
        print("Error: Input files not found.")
        return

    # STEP 1: DETECT THE LIAR
    # We run the analysis before building the map
    print("Analyzing sensor data for bias...")
    biased_sensor = detect_biased_sensor(sensor_data, map_data['T'])
    print(f"Calibration Complete. Treating '{biased_sensor}' as unreliable.")

    # STEP 2: BUILD MAP WITH CORRECTION
    poly_map = PolyvilleMap(map_data, sensor_data, biased_sensor_name=biased_sensor)

    # STEP 3: RUN SCHEDULER (Standard)
    fleet = ["truck1", "truck2", "drone1", "drone2"] 
    scheduler = Scheduler(poly_map, obj_data)
    solution = scheduler.solve(fleet)

    with open('solution.json', 'w') as f:
        json.dump(solution, f, indent=4)
    
    print("Solution generated successfully.")

if __name__ == "__main__":
    main()
