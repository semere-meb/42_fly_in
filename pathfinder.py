from collections import deque

from graph import Graph
from models import Hub


class Pathfinder:
    graph: dict[Hub, dict[Hub, list[float]]]  # {src: {dst: [capacity, cost]}}

    def __init__(self, graph: Graph):
        self.graph = graph.graph

    def bfs(
        self, source: Hub, sink: Hub, parent: dict[Hub, tuple[Hub, float]]
    ) -> bool:
        visited: set[Hub] = {source}
        queue: deque[Hub] = deque([source])

        while queue:
            node = queue.popleft()
            for neighbor, (capactity, cost) in self.graph[node].items():
                if neighbor not in visited and capactity > 0:
                    visited.add(neighbor)
                    parent[neighbor] = (node, cost)
                    if neighbor == sink:
                        return True
                    queue.append(neighbor)
        return False

    def edmonds_karp(
        self, source: Hub, sink: Hub
    ) -> tuple[float, list[tuple[float, float, list[Hub]]]]:
        max_flow: float = 0
        paths: list[tuple[float, float, list[Hub]]] = []

        while True:
            parent: dict[Hub, tuple[Hub, float]] = {}

            if not self.bfs(source, sink, parent):
                break

            path: list[Hub] = []
            path_cost: float = 0
            node: Hub = sink
            while node != source:
                path.append(node)
                node, cost = parent[node]
                path_cost += cost
            path.append(source)
            path.reverse()

            flow: float = min(
                self.graph[path[i]][path[i + 1]][0]
                for i in range(len(path) - 1)
            )

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.graph[u][v][0] -= flow
                self.graph[v][u][0] += flow

            max_flow += flow
            paths.append((flow, path_cost, path))

        return max_flow, paths
