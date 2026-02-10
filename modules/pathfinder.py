import heapq

class PathFinder:
    def __init__(self, environment):
        self.env = environment

    def find_path(self, start_node, start_time, target_node, target_deadline, vehicle_type):
        """
        Returns: (cost, path_list, arrival_time)
        path_list is [node_at_start_time, node_at_start+1, ..., node_at_arrival]
        """
        # Priority Queue: (estimated_total_cost, current_cost, current_node, current_time, path)
        pq = [(0, 0, start_node, start_time, [start_node])]
        
        # Visited: (node, time) -> min_cost
        visited = {}
        
        min_cost_to_target = float('inf')
        best_path = None
        best_arrival_time = -1

        while pq:
            est_total, g_cost, u, t, path = heapq.heappop(pq)

            # Pruning
            if g_cost >= min_cost_to_target:
                continue
            if t > target_deadline:
                continue
            if (u, t) in visited and visited[(u, t)] <= g_cost:
                continue
            visited[(u, t)] = g_cost

            # Goal Check
            if u == target_node:
                if g_cost < min_cost_to_target:
                    min_cost_to_target = g_cost
                    best_path = path
                    best_arrival_time = t
                continue 

            # Stop if we hit max time
            if t + 1 >= self.env.T_max:
                continue

            # Move 1: Wait at current node (Cost 0)
            # Waiting is always allowed and costs 0.
            wait_cost = 0
            heapq.heappush(pq, (g_cost + wait_cost, g_cost + wait_cost, u, t + 1, path + [u]))

            # Move 2: Travel to neighbors
            neighbors = self.env.get_neighbors(u)
            for v, road_type in neighbors:
                travel_cost = self.env.calculate_cost(road_type, t, vehicle_type)
                
                # If cost is infinite (truck flying or time over), skip
                if travel_cost == float('inf'):
                    continue

                new_g = g_cost + travel_cost
                heapq.heappush(pq, (new_g, new_g, v, t + 1, path + [v]))

        return min_cost_to_target, best_path, best_arrival_time
    
