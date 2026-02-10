class PolyvilleMap:
    def __init__(self, map_data, sensor_data, biased_sensor_name=None):
        self.N = map_data['N']
        self.T_max = map_data['T']
        self.adj_matrix = map_data['map']
        
        # Parse road weights keys from string to int for safety
        self.road_weights = {int(k): v for k, v in map_data['road_weights'].items()}
        
        self.sensor_data = sensor_data
        self.biased_sensor = biased_sensor_name 

    def get_neighbors(self, node_id):
        """Returns list of (neighbor_id, road_type)"""
        # Internal Logic is 0-indexed. Input matrix is 0-indexed rows.
        neighbors = []
        row = self.adj_matrix[node_id]
        for target_node, road_type in enumerate(row):
            if road_type != -1:
                neighbors.append((target_node, road_type))
        return neighbors

    def get_reading(self, sensor_type, t):
        """Helper to get a 'Cleaned' reading"""
        val = self.sensor_data[sensor_type][t]
        
        # If this is the biased sensor, we DAMPEN the reading.
        if sensor_type == self.biased_sensor:
            if sensor_type == 'visibility':
                # For Vis, "Bad" is Low. So we boost it to be safer (make it higher).
                return val * 1.5 
            else:
                # For others, "Bad" is High. So we reduce it.
                return val * 0.6 
        return val

    def calculate_cost(self, road_type, t, vehicle_type):
        """
        Calculates traversal cost based on rules.
        """
        if t >= self.T_max:
            return float('inf')

        # Rule: Airspace (0) is always 0 cost for drones
        if road_type == 0:
            if vehicle_type == 'truck':
                return float('inf') # Trucks can't fly
            return 0

        # Base Weight
        weights = self.road_weights.get(road_type, [1])
        w_base = weights[t] if t < len(weights) else weights[-1]

        # Get Cleaned Sensor Data
        wind = self.get_reading('wind', t)
        vis = self.get_reading('visibility', t)
        shock = self.get_reading('earth_shock', t)
        rain = self.get_reading('rainfall', t)

        is_blocked = False

        if vehicle_type == 'truck':
            # Trucks: Earth > 10 AND Rain > 30 
            if (w_base * shock > 10) and (w_base * rain > 30):
                is_blocked = True
        elif vehicle_type == 'drone':
            # Drones: Wind > 60 AND Vis < 6 
            if (w_base * wind > 60) and (w_base * vis < 6):
                is_blocked = True

        # Cost Formula
        cost = w_base * road_type
        if is_blocked:
            cost *= 5
            
        return cost
