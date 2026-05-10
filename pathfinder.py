from typing import List, Tuple

from models import Hub, Map, Zone


class Pathfinder:
    paths: List[List[Hub]]
    path_rank: List[Tuple[int, List[List[Hub]]]] = []
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
                paths.append(path.copy())
            else:
                for adj in current.adj:
                    if adj.zone != Zone.RESTRICTED and adj not in visited:
                        dfs_get_path(adj, visited, path)
            path.pop()
            visited.remove(current)

        dfs_get_path(self.map.end, set(), [])
        self.paths = paths

    def cal_path_cost(self) -> None:
        for path in self.paths:
            cost = 0
