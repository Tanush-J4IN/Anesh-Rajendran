Polyville Disaster Relief: Autonomous Logistics Solver
Event: Tryst '26 Trials

Project Overview
This project implements a solution for a Time-Dependent Vehicle Routing Problem (TD-VRP) within a simulated disaster environment. The objective is to coordinate a mixed fleet of autonomous trucks and drones to deliver supplies to critical nodes. The solver navigates a dynamic graph with time-varying edge weights constrained by weather conditions (Wind, Rain, Visibility, Earth Shocks).

Technical Challenge: Sensor Reliability
The core complexity of this challenge involves noisy sensor data. The environment includes four weather sensors, one of which is statistically biased and unreliable. A standard pathfinding approach would result in suboptimal routing or gridlock due to false positive hazard detection from the faulty sensor.

Methodological Approach
Our solution implements a pre-computation calibration layer to sanitize input data before routing:

Statistical Outlier Detection: The system analyzes the "Hazard Activation Rate" of all sensors over the full time horizon.

Bias Identification: By comparing activation thresholds, the system identifies the sensor exhibiting statistically improbable hazard frequencies (the outlier).

Signal Damping: A damping factor is applied to the identified sensor's readings within the graph logic, reducing false positives while maintaining safety margins.

Heuristic Search: Routes are generated using *A Search (A-Star)** on a Time-Expanded Graph, optimizing for arrival time while accounting for wait-time strategies to bypass temporary weather blocks.

Project Structure
The codebase is organized into modular components to ensure separation of concerns:

main.py: Entry point handling file I/O, fleet detection, and orchestration.

modules/sensor_analysis.py: Performs statistical analysis to identify and flag the biased sensor.

modules/graph.py: Manages the graph state, edge weights, and applies sensor damping logic.

modules/pathfinder.py: Implements the A* search algorithm for optimal path traversal.

modules/scheduler.py: assigning objectives to vehicles based on a greedy heuristic strategy.