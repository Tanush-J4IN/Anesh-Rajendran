import numpy as np

def detect_biased_sensor(sensor_data, T_max):
    """
    Analyzes sensor arrays to find the statistical outlier.
    Returns: The name of the biased sensor (e.g., 'rainfall', 'earth_shock')
    """
    
    # Thresholds from the problem statement
    # We are looking for values that exceed safety limits
    thresholds = {
        'rainfall': 30,
        'earth_shock': 10,
        'wind': 60,
        'visibility': 6  # Special case: Hazard if BELOW this
    }

    # Calculate "Hazard Activation Rate"
    # We assume base_weight is 1 for this statistical check to find the raw sensor bias
    activation_rates = {}

    for sensor_type, data in sensor_data.items():
        if sensor_type not in thresholds:
            continue
            
        readings = np.array(data[:T_max])
        limit = thresholds[sensor_type]
        
        if sensor_type == 'visibility':
            # Count how often visibility is dangerously LOW
            count = np.sum(readings < limit)
        else:
            # Count how often value is dangerously HIGH
            count = np.sum(readings > limit)
            
        activation_rates[sensor_type] = count / T_max

    # Logic: The sensor with the HIGHEST activation rate is likely the "Biased High" sensor.
    sorted_sensors = sorted(activation_rates.items(), key=lambda x: x[1], reverse=True)
    
    suspect = sorted_sensors[0][0]
    rate = sorted_sensors[0][1]
    
    # If the top suspect is active > 50% more often than the next, it's definitely biased.
    # Even if not, the highest one is the safest bet to dampen.
    print(f"DEBUG: Sensor Activation Rates: {activation_rates}")
    print(f"DEBUG: Detected Biased Sensor: {suspect} (Active {rate*100:.1f}% of time)")
    
    return suspect
