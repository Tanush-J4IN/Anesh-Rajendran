from .pathfinder import PathFinder

class Scheduler:
    def __init__(self, map_obj, objectives_data):
        self.map = map_obj
        self.pf = PathFinder(map_obj)
        self.objectives = objectives_data['objectives']
        
        # Convert start node to 0-indexed
        self.internal_start_node = objectives_data['start_node'] - 1 
        
        # Sort objectives by Points (Greedy Strategy)
        self.objectives.sort(key=lambda x: x['points'], reverse=True)

    def solve(self, vehicles):
        """
        vehicles: list of IDs ['truck1', 'truck2', 'drone1']
        """
        # Initialize State
        vehicle_states = {} 
        for v in vehicles:
            vehicle_states[v] = {
                'curr_node': self.internal_start_node,
                'curr_time': 0,
                'path': [self.internal_start_node + 1] # Output 1-based
            }

        completed_objectives = set()

        # Simple Round-Robin Assignment Logic with Greedy Choice
        # We loop until no vehicle can do any more tasks
        
        work_remains = True
        while work_remains:
            work_remains = False # Assume done unless we find a job
            
            for vid in vehicles:
                v_type = 'truck' if 'truck' in vid else 'drone'
                
                # If vehicle reached T_max, skip
                if vehicle_states[vid]['curr_time'] >= self.map.T_max:
                    continue

                best_obj = None
                best_path = None
                best_arrival = -1
                max_profit = -float('inf')

                current_node = vehicle_states[vid]['curr_node']
                current_time = vehicle_states[vid]['curr_time']

                # Look for the best objective for THIS vehicle at THIS time
                for obj in self.objectives:
                    oid = obj['id']
                    if oid in completed_objectives:
                        continue
                    
                    target_node = obj['node'] - 1 # 0-indexed
                    start_window = obj['release']
                    end_window = obj['deadline']
                    
                    # Hard Constraint: If deadline passed, skip
                    if end_window < current_time:
                        continue
                        
                    # Hard Constraint: If we can't physically get there in time (Manhattan heuristic)
                    # This is just an optimization to avoid running A* on impossible tasks
                    # We skip it and trust A* to fail fast.

                    # Run A*
                    cost, path_segment, arrival = self.pf.find_path(
                        current_node, current_time, target_node, end_window, v_type
                    )

                    if path_segment and arrival >= start_window:
                        # Calculate Profit = Points - Cost
                        # (We could subtract late penalties here too if we wanted to be more precise)
                        profit = obj['points'] - cost
                        
                        if profit > max_profit:
                            max_profit = profit
                            best_obj = obj
                            best_path = path_segment
                            best_arrival = arrival

                # If we found a task for this vehicle
                if best_obj:
                    work_remains = True # We did something, so keep looping
                    
                    # Update State
                    # The path_segment includes the start node. We slice [1:] to avoid duplication
                    actual_steps = best_path[1:]
                    
                    for node in actual_steps:
                        vehicle_states[vid]['path'].append(node + 1) # Output 1-based
                    
                    vehicle_states[vid]['curr_node'] = best_path[-1]
                    vehicle_states[vid]['curr_time'] = best_arrival
                    completed_objectives.add(best_obj['id'])
                    
        # Finalization: Pad paths to length T (Wait at final node)
        final_output = {}
        for vid, state in vehicle_states.items():
            path = state['path']
            last_node = path[-1]
            while len(path) <= self.map.T_max: # We need entries for t=0 to t=T (usually T+1 states)
                path.append(last_node)
            
            # Truncate to exactly T+1 (t=0 to t=T) as per example
            # Note: Example JSON showed t=0 to t=T steps.
            final_output[vid] = path[:self.map.T_max + 1] 
            
        return final_output
