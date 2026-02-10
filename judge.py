import json

# --- CONFIGURATION ---
MAP_FILE = 'public_map_2.json'
SENSOR_FILE = 'sensor_data_2.json'
OBJ_FILE = 'objectives_2.json'
SOLUTION_FILE = 'solution.json' # Save your JSON logic here

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def calculate_score():
    # 1. Load Data
    try:
        map_data = load_json(MAP_FILE)
        sensor_data = load_json(SENSOR_FILE)
        obj_data = load_json(OBJ_FILE)
        solution = load_json(SOLUTION_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # 2. Parse Map Data
    adj_matrix = map_data['map']
    road_weights = {int(k): v for k, v in map_data['road_weights'].items()}
    T_max = map_data['T']
    
    total_score = 0
    total_cost = 0
    total_reward = 0
    completed_objectives = set()

    print(f"--- Scoring Report for {SOLUTION_FILE} ---\n")

    # 3. Calculate Travel Costs
    for vid, path in solution.items():
        v_type = 'truck' if 'truck' in vid else 'drone'
        vehicle_cost = 0
        
        # Ensure path matches time length
        path = path[:T_max+1] 
        
        for t in range(len(path) - 1):
            u = path[t] - 1      # Convert to 0-index
            v = path[t+1] - 1    # Convert to 0-index
            
            # Wait Logic (Cost 0)
            if u == v:
                continue
                
            # Get Road Type
            road_type = adj_matrix[u][v]
            if road_type == -1:
                print(f"INVALID MOVE: {vid} moved {u+1}->{v+1} (No road!)")
                return
            
            # Calculate Base Cost
            if road_type == 0:
                step_cost = 0
            else:
                weights = road_weights.get(road_type, [1])
                w_base = weights[t] if t < len(weights) else weights[-1]
                
                # Check Weather (Blocking)
                wind = sensor_data['wind'][t]
                vis = sensor_data['visibility'][t]
                shock = sensor_data['earth_shock'][t]
                rain = sensor_data['rainfall'][t]
                
                is_blocked = False
                if v_type == 'truck':
                    if (w_base * shock > 10) and (w_base * rain > 30):
                        is_blocked = True
                elif v_type == 'drone':
                    if (w_base * wind > 60) and (w_base * vis < 6):
                        is_blocked = True
                
                step_cost = w_base * road_type
                if is_blocked:
                    step_cost *= 5
            
            # Truck Flight Check
            if v_type == 'truck' and road_type == 0:
                print(f"INVALID: Truck flying at t={t}")
                step_cost = float('inf')

            vehicle_cost += step_cost
            
        print(f"Vehicle {vid}: Cost Incurred = {vehicle_cost}")
        total_cost += vehicle_cost

    # 4. Calculate Objective Rewards
    print("\n--- Objectives Completed ---")
    objectives = obj_data['objectives']
    
    for obj in objectives:
        oid = obj['id']
        target = obj['node']
        start = obj['release']
        end = obj['deadline']
        points = obj['points']
        
        # Check if ANY vehicle visited this node in the window
        best_arrival = float('inf')
        
        for vid, path in solution.items():
            # Find earliest valid arrival
            for t, node_id in enumerate(path):
                if node_id == target:
                    if start <= t <= end:
                        if t < best_arrival:
                            best_arrival = t
                            
        if best_arrival != float('inf'):
            # Calculate Score
            late_penalty = 10 * (best_arrival - start)
            reward = points - late_penalty
            
            print(f"Objective {oid}: Completed at t={best_arrival}. Reward: {reward} (Base {points} - Pen {late_penalty})")
            total_reward += reward
            completed_objectives.add(oid)
        else:
            # print(f"Objective {oid}: MISSED")
            pass

    # 5. Final Calculation
    total_score = total_reward - total_cost
    print(f"\n--------------------------------")
    print(f"Total Reward: {total_reward}")
    print(f"Total Cost:   -{total_cost}")
    print(f"FINAL SCORE:  {total_score}")
    print(f"--------------------------------")

if __name__ == "__main__":
    calculate_score()
4
