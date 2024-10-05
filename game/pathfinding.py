# game/pathfinding.py

import heapq

class Node:
    def __init__(self, x, y, walkable=True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g = float('inf')  # Cost from start to current node
        self.h = 0  # Heuristic cost from current node to end
        self.f = float('inf')  # Total cost
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    """Calculate the Manhattan distance heuristic."""
    return abs(a.x - b.x) + abs(a.y - b.y)

def get_neighbors(node, grid, width, height):
    """Retrieve walkable neighboring nodes."""
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
    for dx, dy in directions:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbor = grid[ny][nx]
            if neighbor.walkable:
                neighbors.append(neighbor)
    return neighbors

def a_star_search(grid, start, end, width, height):
    """Perform A* pathfinding from start to end."""
    open_set = []
    heapq.heappush(open_set, start)
    start.g = 0
    start.f = heuristic(start, end)
    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)

        if current == end:
            # Reconstruct path
            path = []
            while current.parent:
                path.append((current.x, current.y))
                current = current.parent
            path.reverse()
            return path

        closed_set.add((current.x, current.y))

        for neighbor in get_neighbors(current, grid, width, height):
            if (neighbor.x, neighbor.y) in closed_set:
                continue

            tentative_g = current.g + 1  # Assuming uniform cost

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, end)
                neighbor.f = neighbor.g + neighbor.h
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)

    return []  # No path found
