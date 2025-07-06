import heapq
import math
import time
import matplotlib.pyplot as plt
import numpy as np

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g_cost = 0
        self.h_cost = 0
        self.f_cost = 0

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __eq__(self, other):
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

def diagonal_distance(current_pos, goal_pos):
    dx = abs(current_pos[0] - goal_pos[0])
    dy = abs(current_pos[1] - goal_pos[1])
    return max(dx, dy)

def a_star_search(grid_costs, start_pos, goal_pos, dimensions):
    start_time = time.time()
    max_row, max_col = dimensions

    start_node = Node(start_pos)
    goal_node = Node(goal_pos)

    start_node.h_cost = diagonal_distance(start_node.position, goal_node.position)
    start_node.f_cost = start_node.g_cost + start_node.h_cost

    open_list = []
    heapq.heappush(open_list, start_node)

    visited_costs = {start_node.position: start_node.g_cost}

    parents = {start_node.position: None}

    movements = [
        (-1, 0, False), (1, 0, False), (0, -1, False), (0, 1, False),
        (-1, -1, True), (-1, 1, True), (1, -1, True), (1, 1, True)
    ]

    while open_list:
        current_node = heapq.heappop(open_list)

        if current_node.position == goal_node.position:
            path = []
            temp = current_node
            while temp is not None:
                path.append(temp.position)
                parent_pos = parents.get(temp.position)
                temp = parent_pos
            runtime = time.time() - start_time
            return path[::-1], current_node.g_cost, runtime

        for dr, dc, is_diagonal in movements:
            neighbor_pos = (current_node.position[0] + dr, current_node.position[1] + dc)

            if not (0 <= neighbor_pos[0] < max_row and 0 <= neighbor_pos[1] < max_col):
                continue
            if neighbor_pos not in grid_costs:
                continue

            terrain_cost = grid_costs[neighbor_pos]
            move_cost = (1.4 * terrain_cost) if is_diagonal else terrain_cost
            new_g_cost = current_node.g_cost + move_cost

            if neighbor_pos not in visited_costs or new_g_cost < visited_costs[neighbor_pos]:
                visited_costs[neighbor_pos] = new_g_cost

                neighbor_node = Node(neighbor_pos)
                neighbor_node.g_cost = new_g_cost
                neighbor_node.h_cost = diagonal_distance(neighbor_pos, goal_node.position)
                neighbor_node.f_cost = neighbor_node.g_cost + neighbor_node.h_cost

                parents[neighbor_pos] = current_node

                heapq.heappush(open_list, neighbor_node)

    runtime = time.time() - start_time
    return None, 0, runtime

def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    m, n = map(int, lines[0].split())
    dimensions = (m, n)

    k = int(lines[1])
    obstacles = set()
    obstacle_lines = lines[2 : 2 + k]
    for line in obstacle_lines:
        x, y = map(int, line.split())
        obstacles.add((x, y))

    c = int(lines[2 + k])
    terrain_costs_input = {}
    terrain_lines = lines[3 + k : 3 + k + c]
    for line in terrain_lines:
        x, y, cost = map(int, line.split())
        terrain_costs_input[(x, y)] = cost

    start_x, start_y = map(int, lines[3 + k + c].split())
    start_pos = (start_x, start_y)

    goal_x, goal_y = map(int, lines[4 + k + c].split())
    goal_pos = (goal_x, goal_y)

    grid_costs = {}
    for r in range(m):
        for col in range(n):
            pos = (r, col)
            if pos not in obstacles:
                grid_costs[pos] = terrain_costs_input.get(pos, 1)

    return grid_costs, start_pos, goal_pos, dimensions, obstacles, terrain_costs_input

def plot_grid(dimensions, grid_costs, obstacles, terrain_costs_input, start_pos, goal_pos, path):
    m, n = dimensions
    vis_grid = np.ones((m, n)) * 1.0

    for r in range(m):
        for c_ in range(n):
            pos = (r, c_)
            if pos in obstacles:
                vis_grid[r, c_] = np.nan
            elif pos in terrain_costs_input:
                vis_grid[r, c_] = terrain_costs_input[pos]

    fig, ax = plt.subplots(figsize=(8, 8))

    cmap = plt.cm.viridis
    cmap.set_bad(color='black')

    valid_costs = [c for c in vis_grid.flatten() if not np.isnan(c)]
    vmin = min(valid_costs) if valid_costs else 1
    vmax = max(valid_costs) if valid_costs else 1

    cax = ax.imshow(vis_grid, cmap=cmap, origin='lower', vmin=vmin, vmax=vmax * 1.1)

    ax.set_xticks(np.arange(-.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-.5, m, 1), minor=True)
    ax.grid(which="minor", color="grey", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(np.arange(0, n, 1))
    ax.set_yticks(np.arange(0, m, 1))

    ax.plot(start_pos[1], start_pos[0], 'go', markersize=12, label='Start')
    ax.plot(goal_pos[1], goal_pos[0], 'ro', markersize=12, label='Goal')

    if path:
        path_rows = [p[0] for p in path]
        path_cols = [p[1] for p in path]
        ax.plot(path_cols, path_rows, 'b-', linewidth=3, label='Path')

    ax.legend()
    fig.colorbar(cax, label='Terrain Cost (Black=Obstacle)')
    plt.title("A* Pathfinding Result (Simplified)")
    plt.xlabel("Column")
    plt.ylabel("Row")
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, m - 0.5)
    plt.show()

if __name__ == "__main__":
    input_content = """10 10    # Grid dimensions
                        8       # Number of obstacle cells
                        2 3     #Obstacle coordinate start
                        3 3     #       ---
                        4 3     #       ---
                        3 6     #       ---
                        6 2     #       ---
                        6 7     #       ---
                        7 7     #       ---
                        8 5     #Obstacle coordinate end
                        5       # Number of terrain cost cells
                        1 5 3   # Terrain costs(default is 1 if not specified)
                        5 1 4   # Terrain costs(default is 1 if not specified)
                        4 6 5   # Terrain costs(default is 1 if not specified)
                        7 4 2   # Terrain costs(default is 1 if not specified)
                        8 8 6   # Terrain costs(default is 1 if not specified)
                        0 0     # Starting cell
                        9 9     # Goal cell
                        """

    lines = [line.strip() for line in input_content.strip().split('\n') if line.strip()]

    m, n = map(int, lines[0].split())
    dimensions = (m, n)

    k = int(lines[1])
    obstacles = set()
    obstacle_lines = lines[2 : 2 + k]
    for line in obstacle_lines:
        x, y = map(int, line.split())
        obstacles.add((x, y))

    c = int(lines[2 + k])
    terrain_costs_input = {}
    terrain_lines = lines[3 + k : 3 + k + c]
    for line in terrain_lines:
        x, y, cost = map(int, line.split())
        terrain_costs_input[(x, y)] = cost

    start_x, start_y = map(int, lines[3 + k + c].split())
    start_pos = (start_x, start_y)

    goal_x, goal_y = map(int, lines[4 + k + c].split())
    goal_pos = (goal_x, goal_y)

    grid_costs = {}
    for r in range(m):
        for col in range(n):
            pos = (r, col)
            if pos not in obstacles:
                grid_costs[pos] = terrain_costs_input.get(pos, 1)

    print("Running A* search...")
    path, total_cost, runtime = a_star_search(grid_costs, start_pos, goal_pos, dimensions)

    print("\n--- A* Search Results ---")
    if path:
        print(f"Path Found ({len(path)} steps):")
        if len(path) > 20:
             print(f"  {path[:10]} ... {path[-10:]}")
        else:
             print(f"  {path}")
        print(f"Total Cost: {total_cost:.2f}")
    else:
        print("Path not found.")
    print(f"Runtime: {runtime:.6f} seconds")

    print("\nGenerating plot...")
    plot_grid(dimensions, grid_costs, obstacles, terrain_costs_input, start_pos, goal_pos, path)


