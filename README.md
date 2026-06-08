*This project has been created as part of the 42 curriculum by semebrah.*

*Project version* **1.4**

# Fly-in: Autonomous Drone Routing & Scheduling Simulator

Fly-in is an efficient drone routing system. It simulates scheduling and navigating a fleet of drones from a central starting hub to a target destination through a network of connected zones under tight spatial and temporal constraints.

---

## Table of Contents
1. [Description](#description)
2. [Architecture & Design](#architecture--design)
3. [Algorithmic Approach](#algorithmic-approach)
   - [1. Node-Splitting Flow Network](#1-node-splitting-flow-network)
   - [2. Multi-Path Edmonds-Karp Flow Finder](#2-multi-path-edmonds-karp-flow-finder)
   - [3. Cost-Staggering Scheduler](#3-cost-staggering-scheduler)
4. [Visual Representation](#visual-representation)
5. [Instructions](#instructions)
6. [Resources](#resources)

---

## Description

The main goal of this project is to move all drones from the start zone to the end zone in the minimum number of simulation turns. The project conforms strictly to the following constraints:
* **No Graph Libraries**: Native implementation of the entire graph logic, paths, flows, and schedules (e.g., no NetworkX).
* **Robust Constraints**: Enforces turn-by-turn zone occupancy limits (`max_drones`) and connection capacity limits (`max_link_capacity`).
* **Zone Penalties**: Handles dynamic movement costs based on zone type (`normal` = 1 turn, `restricted` = 2 turns, `priority` = 1 turn preferred, `blocked` = inaccessible).
* **Strict Quality Standards**: 100% typesafe and compliant with MyPy static analysis and Flake8/Ruff coding standards.

---

## Architecture & Design

The project uses a highly modular, decoupled object-oriented architecture:
* **`models.py`**: Defines standard Pydantic models representing the components (`Hub`, `Connection`, `Drone`, `Map`). Ensures data integrity and structural validation upon parsing.
* **`parser.py`**: Reads and validates map files, processes metadata attributes (e.g., zones, max occupancy, and link capacities), and builds the validated state objects.
* **`graph.py`**: Transforms the map network into an augmented, capacity-bounded Flow Network.
* **`pathfinder.py`**: Runs shortest-path maximum flow algorithms to identify disjoint and overlapping routing lanes.
* **`scheduler.py`**: Allocates paths to drones and inserts virtual queue delay-states to schedule collision-free movements.
* **`engine.py`**: Runs the discrete-time step simulation, printing turn-by-turn routing logs.
* **`visualizer.py` & `drone_sprite.py`**: Provides an interactive, beautiful 2D graphical display of the network and drone movement.

---

## Algorithmic Approach

### 1. Node-Splitting Flow Network
Standard maximum flow algorithms bound capacities on graph edges. However, the simulation limits capacities on *vertices* (each hub zone has a `max_drones` capacity limit). 

To natively integrate node capacities into flow pathfinding, we implement a **Node-Splitting Technique** in `graph.py`:
* Every zone/hub $H$ is split into two nodes: an input node $H_{in}$ and an output node $H_{out}$.
* A directed internal edge is added from $H_{in}$ to $H_{out}$ with:
  $$\text{capacity} = \text{max\_drones}(H)$$
  $$\text{cost} = 0$$
* For a **restricted** zone (which takes 2 turns to traverse), a third node $H_{mid}$ is inserted:
  $$H_{in} \xrightarrow{\text{capacity}} H_{mid} \xrightarrow{\text{capacity}} H_{out}$$
* Bi-directional connection links between different hubs $A$ and $B$ are mapped as directed edges:
  $$A_{out} \xrightarrow{\text{max\_link\_capacity}} B_{in}$$
  $$B_{out} \xrightarrow{\text{max\_link\_capacity}} A_{in}$$
* Edge costs are weighted by destination zone types:
  * `restricted`: `2.0`
  * `priority`: `0.99` (preferred in Dijkstra/BFS searches)
  * `normal`: `1.0`

### 2. Multi-Path Edmonds-Karp Flow Finder
To find the optimal routing channels, `pathfinder.py` implements the **Edmonds-Karp Algorithm** (an implementation of the Ford-Fulkerson method using Breadth-First Search):
1. **Augmenting Paths**: It iteratively runs a BFS to find the shortest path from the source $S_{out}$ to the sink $T_{in}$ that has positive residual capacity.
2. **Bottleneck Evaluation**: For each discovered path, it computes the bottleneck capacity (the minimum residual capacity along its constituent nodes and connections).
3. **Residual Graph Update**: It updates the residual capacities by subtracting the bottleneck flow from the forward edges and adding it to the backward (reverse) edges.
4. This yields a set of optimal, capacity-bounded path channels supporting concurrent drone flows.

### 3. Cost-Staggering Scheduler
Once the available multi-path flow channels are discovered, `scheduler.py` manages the assignment and turn scheduling of individual drones:
* **Iterative Allocation**: Drones are allocated in batches up to the path's bottleneck flow capacity.
* **Collision-Free Queueing (Staggering)**: When multiple drones are assigned to the same path channel, they cannot start simultaneously without violating the node capacity limits. To resolve this, after assigning drones to a path, the path's virtual cost is incremented by `1` (`path.cost += 1`), and a delay is introduced by inserting the starting hub at the prefix of subsequent paths:
  $$\text{path.hubs.insert}(0, \text{start\_hub})$$
  This shifts the traversal schedule of succeeding drones by exactly 1 turn, acting as a virtual staging queue that guarantees drones never collide at bottlenecks.
* **Path Alignment**: Finally, all paths are padded at the tail with the destination hub to align with the longest path's length, enabling simple turn-by-turn execution.

---

## Visual Representation

The application features a beautifully polished, interactive 2D graphical visualizer powered by the **Arcade** and **Pyglet** libraries:
* **Distinct Node Visuals**: Nodes/hubs are represented with stylized sprites (Meteors) colored and shaped differently based on their zone types:
  * `normal`: Grey/default
  * `priority`: Green
  * `restricted`: Yellow
  * `blocked`: Red
* **Real-time Metrics**: Hub labels display live occupancy counters (e.g., `current_drones / max_drones`). Connection link lines adjust their thickness representing their bandwidth capacities.
* **Keyboard Navigation**:
  * `Right Arrow`: Progresses the simulation forward by one turn.
  * `Left Arrow`: Rewinds the simulation backward by one turn.
  * `R`: Resets the simulation to the initial starting state.
  * `Q`: Gracefully exits the application.
* **Pure Stateless Design**: The visualization coordinates, hub occupancies, and connection statuses are computed **deterministically and statelessly** from the turn index. This guarantees robust and visual-perfect rendering when scrubbing forward or backward through turns.

---

## Example Input & Expected Output

### Example Input (`maps/easy/01_linear_path.txt`)
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 0 3 [color=yellow]
hub: waypoint1 0 1 [color=blue]
hub: waypoint2 0 2 [color=blue]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Expected Output
```text
D0-<waypoint1>
D0-<waypoint2> D1-<waypoint1>
D0-<goal> D1-<waypoint2>
D0-<goal> D1-<goal>
```

---

## Instructions

### Installation
Install project dependencies isolated in a virtual environment using the Makefile:
```bash
make install
```

### Running the Simulator
Run the main script using the default map:
```bash
make run
```
To run the simulation with a specific custom map, use:
```bash
uv run python main.py -m <path_to_map_file>
```

### Static Analysis & Testing
Ensure total typesafety, formatting consistency, and error safety using the linting targets:
```bash
# Run flake8, ruff check, and strict mypy typechecking
make lint

# Run strict type checking
make lint-strict

# Run formatting tool
make format
```

---

## Resources

### Theoretical References
* **Network Flows**: [Introduction to Algorithms (CLRS) - Maximum Flow](https://en.wikipedia.org/wiki/Maximum_flow_problem)
* **Edmonds-Karp Algorithm**: [BFS-based Ford-Fulkerson Method](https://en.wikipedia.org/wiki/Edmonds%E2%80%93Karp_algorithm)
* **Vertex Capacities**: [Reduction of Node-Capacities to Edge-Capacities (Node Splitting)](https://en.wikipedia.org/wiki/Node-splitting_technique)

### AI Usage Description
In accordance with the 42 AI usage guidelines, AI assistance was leveraged as a collaborative peer-learning partner to reduce boilerplate work and clarify edge behaviors:
1. **Design Optimization**: Used to brainstorm optimal strategies for converting node capacities to edge capacities, which led to the elegant node-splitting flow design.
