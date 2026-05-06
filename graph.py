import heapq
from typing import Dict

from constants import inf
from models import Map, Zone


class Graph:
    """

    This class represents the map in an adjacency list and provides methods to
    compute the shortest path from a source hub to other reachable hubs.

    """

    adj: Dict[str, Dict[str, float]]
    map: Map

    def __init__(self, map: Map):
        self.map = map
        self.adj = self.get_adj(map)

    def get_adj(self, map: Map) -> Dict[str, Dict[str, float]]:
        """

        Args:
          map: Map: The map definition of the entire simulation.

        Returns: The adjacency list of a node to all other hub it is connected
            with.

        """
        adj: Dict[str, Dict[str, float]] = {hub.name: {} for hub in map.hubs}

        for connection in map.connections:
            hub1, hub2 = connection.hubs

            for src, dest in [(hub1, hub2), (hub2, hub1)]:
                if dest.zone == Zone.PRIORITY:
                    weight = 1
                elif dest.zone == Zone.NORMAL:
                    weight = 1.1
                elif dest.zone == Zone.RESTRICTED:
                    weight = 2
                elif dest.zone == Zone.BLOCKED:
                    weight = inf
                adj[src.name][dest.name] = weight

        return adj

    def dijkstra(self, src_hub_name: str) -> Dict[str, float] | None:
        """

        Computest shortest path from the hub with start_name name to all other
        reachable hubs.

        Args:
          src_hub_name: str: The name of the source hub to start distance
              computing.

        Returns: The distance to all reachable nodes, None if no hub exists
            with name src_hub_name.

        """
        if src_hub_name not in self.adj:
            return None

        pq = []

        dist: Dict[str, float] = {
            hub.name: float(inf) for hub in self.map.hubs
        }

        dist[src_hub_name] = 0
        heapq.heappush(pq, (0, src_hub_name))

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                continue

            for v, w in self.adj[u].items():
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], v))

        self.dist = dist
        return dist
