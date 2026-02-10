import json
import os
import sys

# Import our modules
from modules.graph import PolyvilleMap
from modules.scheduler import Scheduler
from modules.sensor_analysis import detect_biased_sensor

def load_json(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found in current directory.")
        sys.exit(1)
    with open(filename, 'r') as f:
        return json.load(f)

def generate_fleet(obj_data):
    """
    Reads 'trucks' and 'drones' counts from objectives.json
    Returns a list like ['truck1', 'truck2', 'drone1']
    """
    fleet = []
    num_trucks = obj_data.get('trucks', 0)
    num_drones = obj_data.get('drones', 0)
    
    for i in range(1, num_trucks + 1):
        fleet.append(f"truck{i}")
    for i in range(1, num_drones + 1):
        fleet.append(f"drone{i}")
        
    print(f"Fleet detected: {fleet}")
    return fleet

def main():
    print("--- Polyville Disaster Relief Solver ---")
    
    # 1. Load Data
    # Ensure these files are in the same directory as main.py
    map_data = load_json('public_map_2.json')
    sensor_data = load_json('sensor_data_2.json')
    obj_data = load_json('objectives_2.json')

    # 2. Sensor Analysis (The Twist)
    print("Analyzing sensor data for bias...")
    biased_sensor = detect_biased_sensor(sensor_data, map_data['T'])
    print(f"Calibration Complete. Damping factor applied to '{biased_sensor}'.")

    # 3. Build Environment
    poly_map = PolyvilleMap(map_data, sensor_data, biased_sensor_name=biased_sensor)

    # 4. Determine Fleet
    fleet = generate_fleet(obj_data)

    # 5. Run Scheduler
    print("Calculating optimal routes...")
    scheduler = Scheduler(poly_map, obj_data)
    solution = scheduler.solve(fleet)

    # 6. Save Output
    output_file = 'solution.json'
    with open(output_file, 'w') as f:
        json.dump(solution, f, indent=4)
    
    print(f"Success! Solution saved to {output_file}")

if __name__ == "__main__":
    main()
