from typing import List, Tuple

from models import Connection, Hub, Map, Zone


class Pathfinder:
    paths: List[List[Hub]]
    # length, throughput, cost, path
    path_rank: List[Tuple[int, int, float, List[Hub]]] = []
    map: Map

    def __init__(self, map: Map):
        self.map = map

    def get_all_paths(self) -> None:

        paths: List[List[Hub]] = []

        def dfs_get_path(
            current: Hub,
            visited: set[Hub],
            path: List[Hub],
        ):
            visited.add(current)
            path.append(current)

            if current.is_start:
                candidate_path = path.copy()
                candidate_path.reverse()
                paths.append(candidate_path)
            else:
                for adj in current.adj:
                    if adj.zone != Zone.BLOCKED and adj not in visited:
                        dfs_get_path(adj, visited, path)
            path.pop()
            visited.remove(current)

        dfs_get_path(self.map.end, set(), [])
        self.paths = paths

    def get_conn(self, hub1: Hub, hub2: Hub) -> Connection | None:
        for conn in self.map.connections:
            if set(conn.hubs) == set([hub1, hub2]):
                return conn
        return None

    def cal_path_cost(self) -> None:
        for path in self.paths:
            cost = 0
            min_conn_capacitiy = float("inf")

            for i in range(len(path) - 1):
                conn = self.get_conn(path[i], path[i + 1])
                if conn:
                    if path[i + 1].zone == Zone.RESTRICTED:
                        cost += 2
                    if path[i + 1].zone == Zone.PRIORITY:
                        cost += 0.999
                    else:
                        cost += 1
                    min_conn_capacitiy = min(
                        min_conn_capacitiy, conn.max_link_capacity
                    )
            min_hub_capacity = min(hub.max_drones for hub in path)

            length = len(path) - 1
            throughput = int(min(min_hub_capacity, min_conn_capacitiy))
            self.path_rank.append((length, throughput, cost, path))
        self.path_rank = sorted(self.path_rank, key=lambda x: x[2])
        self.path_rank = self.path_rank[
            : min(len(self.path_rank), self.map.nb_drones)
        ]
