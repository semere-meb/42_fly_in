from models import Drone, Hub, Map
from pathfinder import Path


class Scheduler:
    """
    Scheduler class to the paths from pathfinder.
    """

    paths: list[Path] = []
    drones: list[Drone]
    map: Map

    def __init__(
        self,
        map: Map,
        paths: list[Path],
    ):
        self.map = map
        self.drones = map.drones
        for path in paths:
            hubs: list[Hub] = []
            for n in path.hubs:
                name, hub_type = n.name.split("-")
                hub = self.map.get_hub(name)
                if hub not in hubs:
                    hubs.append(hub)
                if hub_type == "mid":
                    hubs.append(hub)

            self.paths.append(Path(path.flow, path.cost, hubs))

    def assign_paths(self) -> None:
        """
        Assigns the drones to the paths using staggering after reranking after
        assignments based on cost.
        """
        i = 0
        while i < len(self.drones):
            self.paths.sort(key=lambda path: path.cost)
            path = self.paths[0]

            for j in range(path.flow):
                self.drones[i + j].path = path.hubs.copy()
            path.cost += 1
            path.hubs.insert(0, self.map.start)
            i += path.flow

        self.align_paths()

    def align_paths(self) -> None:
        """
        Padds the paths with the end hub to the length of the longest
        path so as to easily add and remove drones from hubs.
        """
        max_turn = max(len(path.hubs) for path in self.paths) - 1

        for drone in self.drones:
            for _ in range(max_turn - len(drone.path)):
                drone.path.append(self.map.end)
