from collections import deque
from dataclasses import dataclass

from graph import Graph
from models import Hub


@dataclass
class Path:
    """
    A simple class to represents a path and its cost and flow metadata.
    """

    flow: int
    cost: float
    hubs: list[Hub]


class Pathfinder:
    """

    A class to find and contain strategic paths.
    """

    graph: dict[Hub, dict[Hub, list[float]]]

    max_flow: int

    def __init__(self, graph: Graph):
        self.graph = graph.graph
        self.max_flow = 0

    def bfs(
        self, source: Hub, sink: Hub, parent: dict[Hub, tuple[Hub, float]]
    ) -> bool:
        """

        bfs to augument the path, advance to the next breadth/neighbors.

        Args:
          source: Hub: The start hub.
          sink: Hub: The end hub.
          parent: dict[Hub, tuple[Hub, float]]: The previous hub and the cost
            between the current one.

        Returns: returns true on reaching the end hub.

        """
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

    def get_paths(self, source: Hub, sink: Hub) -> list[Path]:
        """
        A max-flow algorithm to find the shortest flow-carrying paths.


        Args:
          source: Hub: the source hub.
          sink: Hub: the destination hub.

        Returns: a list of the strategic (shortest flow-carrying) paths.

        """
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

            self.max_flow += flow
            paths.append(Path(flow, path_cost, path))

        return paths
