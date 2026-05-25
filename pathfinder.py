from collections import deque
from dataclasses import dataclass

from graph import Graph
from models import Hub


@dataclass
class Path:
    flow: int
    cost: float
    hubs: list[Hub]


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

    def edmonds_karp(self, source: Hub, sink: Hub) -> tuple[float, list[Path]]:
        max_flow: int = 0
        paths: list[Path] = []

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

            flow: int = int(
                min(
                    self.graph[path[i]][path[i + 1]][0]
                    for i in range(len(path) - 1)
                )
            )

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.graph[u][v][0] -= flow
                self.graph[v][u][0] += flow

            max_flow += flow
            paths.append(Path(flow, path_cost, path))

        return max_flow, paths
